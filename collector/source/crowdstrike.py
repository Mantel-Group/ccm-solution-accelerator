from falconpy import Hosts, SpotlightVulnerabilities, ZeroTrustAssessment, HostGroup

class SpotlightCursorExpiredError(Exception):
    """Raised when the Spotlight pagination cursor has expired (404)."""
import pandas as pd
import time
import datetime
from dotenv import load_dotenv
import logging
import sys
import os
import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s'
)

class Source:
    def __init__(self, C):
        self.collector = C
        
        if C.env({
                'FALCON_CLIENT_ID': None,
                'FALCON_SECRET': None
            }):
            self.host_list = []
            if self.hosts().empty:
                self.collector.write_blank('crowdstrike_hosts'                       , self._hosts({}))

            if self.zero_trust_assessment().empty:
                self.collector.write_blank('crowdstrike_zero_trust_assessment'       , self._zero_trust_assessment({}))
                self.collector.write_blank('crowdstrike_zero_trust_assessment_items' , self._signals({},None,{}))

            if self.vulnerabilities().empty:
                self.collector.write_blank('crowdstrike_vulnerabilities'             , self._vulnerabilities({}))
                self.collector.write_blank('crowdstrike_vulnerabilities_remediation' , self._remediation({},{}))

            if self.host_groups().empty:
                self.collector.write_blank('crowdstrike_host_groups'                 , self._host_groups({}))

        else:
            self.collector.write_blank('crowdstrike_hosts'                       , self._hosts({}))
            self.collector.write_blank('crowdstrike_host_groups'                 , self._host_groups({}))
            self.collector.write_blank('crowdstrike_vulnerabilities'             , self._vulnerabilities({}))
            self.collector.write_blank('crowdstrike_vulnerabilities_remediation' , self._remediation({},{}))
            self.collector.write_blank('crowdstrike_zero_trust_assessment'       , self._zero_trust_assessment({}))
            self.collector.write_blank('crowdstrike_zero_trust_assessment_items' , self._signals({},None,{}))

    def _call_with_retry(self, func, *args, **kwargs):
        """Call a FalconPy function with connection retry and 429 backoff."""
        max_connect_retries = 2
        max_rate_limit_retries = 5
        rate_limit_wait = 1
        rate_limit_retries = 0
        connect_attempts = 0

        while True:
            try:
                result = func(*args, **kwargs)
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.ChunkedEncodingError) as e:
                connect_attempts += 1
                if connect_attempts <= max_connect_retries:
                    logging.warning(f"Connection error (attempt {connect_attempts}/{max_connect_retries + 1}). Retrying in 5s: {e}")
                    time.sleep(5)
                    continue
                logging.error(f"Connection failed after {max_connect_retries + 1} attempts: {e}")
                raise

            if result["status_code"] == 429:
                rate_limit_retries += 1
                if rate_limit_retries <= max_rate_limit_retries:
                    logging.warning(f"Rate limit hit (429). Retrying in {rate_limit_wait}s (attempt {rate_limit_retries}/{max_rate_limit_retries}).")
                    time.sleep(rate_limit_wait)
                    rate_limit_wait = min(rate_limit_wait * 2, 60)
                    continue
                logging.error(f"Rate limit retries exhausted after {max_rate_limit_retries} attempts.")
                raise Exception("CrowdStrike rate limit retries exhausted")

            return result

    def _host_groups(self,item):
        return {
            "id"                    : item.get("id"),
            "group_type"            : item.get("group_type"),
            "name"                  : item.get("name"),
            "description"           : item.get("description"),
            "assignment_rule"       : item.get("assignment_rule",""),
            "created_by"            : item.get("created_by"),
            "created_timestamp"     : datetime.datetime.strptime(item["created_timestamp"].split('.')[0], "%Y-%m-%dT%H:%M:%S") if item.get("created_timestamp") else pd.NaT,
            "modified_by"           : item.get("modified_by"),
            "modified_timestamp"    : datetime.datetime.strptime(item["modified_timestamp"].split('.')[0], "%Y-%m-%dT%H:%M:%S") if item.get("modified_timestamp") else pd.NaT,
        }

    def host_groups(self):
        logging.info('crowdstrike - host_groups')
        falcon = HostGroup(
            client_id=os.environ["FALCON_CLIENT_ID"],
            client_secret=os.environ["FALCON_SECRET"]
        )
        OFFSET = 0
        TOTAL = 1
        LIMIT = 500
        while OFFSET < TOTAL:
            result = self._call_with_retry(falcon.queryHostGroups, limit=LIMIT, offset=OFFSET)
            if result["status_code"] != 200:
                logging.error(f"crowdstrike host_groups: API returned {result['status_code']}")
                raise Exception(f"crowdstrike host_groups API error: {result['status_code']}")

            OFFSET = result["body"]["meta"]["pagination"]["offset"]
            TOTAL = result["body"]["meta"]["pagination"]["total"]
            returned_device_list = result["body"]["resources"]

            if returned_device_list:
                self.host_list.append(returned_device_list)
                groups_result = self._call_with_retry(falcon.get_host_groups, parameters={"ids": returned_device_list})
                if groups_result["status_code"] != 200:
                    logging.error(f"crowdstrike get_host_groups: API returned {groups_result['status_code']}")
                    raise Exception(f"crowdstrike get_host_groups API error: {groups_result['status_code']}")
                host_groups_response = groups_result["body"]["resources"]
                logging.info(f"Offset {OFFSET}/{TOTAL}: retrieved {len(host_groups_response)} records")
                df = pd.DataFrame([self._host_groups(item) for item in host_groups_response])
                self.collector.store_df('crowdstrike_host_groups', df)

        self.collector.write_df('crowdstrike_host_groups')
        return self.collector.df.get('crowdstrike_host_groups', pd.DataFrame())

    def _hosts(self,item):
        return {
            "client_id"                     : item.get("cid"),
            "device_id"                     : item.get("device_id"),
            "hostname"                      : item.get("hostname"),
            "kernel_version"                : item.get("kernel_version"),
            "last_login_timestamp"          : datetime.datetime.strptime(item["last_login_timestamp"], "%Y-%m-%dT%H:%M:%SZ") if item.get("last_login_timestamp") else pd.NaT,
            "local_ip"                      : item.get("local_ip"),
            "mac_address"                   : item.get("mac_address"),
            "last_login_uid"                : item.get("last_login_uid"),
            "last_login_user"               : item.get("last_login_user"),
            "first_seen"                    : datetime.datetime.strptime(item["first_seen"], "%Y-%m-%dT%H:%M:%SZ") if item.get("first_seen") else pd.NaT,
            "last_seen"                     : datetime.datetime.strptime(item["last_seen"], "%Y-%m-%dT%H:%M:%SZ") if item.get("last_seen") else pd.NaT,
            "os_build"                      : item.get("os_build"),
            "os_version"                    : item.get("os_version"),
            "platform_name"                 : item.get("platform_name"),
            "provision_status"              : item.get("provision_status"),
            "reduced_functionality_mode"    : item.get("reduced_functionality_mode", False),
            "serial_number"                 : item.get("serial_number"),
            "host_status"                   : item.get("status"),
            "system_manufacturer"           : item.get("system_manufacturer"),
            "system_product_name"           : item.get("system_product_name"),
        }

    def hosts(self):
        logging.info('crowdstrike - hosts')
        falcon = Hosts(
            client_id=os.environ["FALCON_CLIENT_ID"],
            client_secret=os.environ["FALCON_SECRET"]
        )
        OFFSET = 0
        TOTAL = 1
        LIMIT = 500
        while OFFSET < TOTAL:
            result = self._call_with_retry(falcon.query_devices_by_filter, limit=LIMIT, offset=OFFSET)
            if result["status_code"] != 200:
                logging.error(f"crowdstrike hosts: API returned {result['status_code']}")
                raise Exception(f"crowdstrike hosts API error: {result['status_code']}")

            OFFSET = result["body"]["meta"]["pagination"]["offset"]
            TOTAL = result["body"]["meta"]["pagination"]["total"]
            returned_device_list = result["body"]["resources"]

            if returned_device_list:
                self.host_list.append(returned_device_list)
                detail_result = self._call_with_retry(falcon.get_device_details, ids=returned_device_list)
                if detail_result["status_code"] != 200:
                    logging.error(f"crowdstrike get_device_details: API returned {detail_result['status_code']}")
                    raise Exception(f"crowdstrike get_device_details API error: {detail_result['status_code']}")
                host_detail = detail_result["body"]["resources"]
                logging.info(f"Offset {OFFSET}/{TOTAL}: retrieved {len(host_detail)} records")
                df = pd.DataFrame([self._hosts(item) for item in host_detail])
                self.collector.store_df('crowdstrike_hosts', df)

        self.collector.write_df('crowdstrike_hosts')
        return self.collector.df.get('crowdstrike_hosts', pd.DataFrame())

    def _remediation(self,item,entity):
        return {
            "id"            : item.get("id"),
            "action"        : entity.get("action",""),
            "entity_id"     : entity.get("id",""),
            "link"          : entity.get("link",""),
            "reference"     : entity.get("reference",""),
            "title"         : entity.get("title",""),
            "vendor_url"    : entity.get("vendor_url",""),
        }

    def _vulnerabilities(self,item):
        return {
            "id"                            : item.get("id"),
            "agent_id"                      : item.get("aid"),
            "client_id"                     : item.get("cid"),
            "status"                        : item.get("status"),
            "cve_id"                        : item.get("cve", {}).get("id"),
            "description"                   : item.get("cve", {}).get("description"),
            "exprt_rating"                  : item.get("cve", {}).get("exprt_rating"),
            "remediation_level"             : item.get("cve", {}).get("remediation_level"),
            "severity"                      : item.get("cve", {}).get("severity"),
            "vector"                        : item.get("cve", {}).get("vector"),
            "created_at"                    : datetime.datetime.strptime(item.get("created_timestamp"), "%Y-%m-%dT%H:%M:%SZ") if item.get("created_timestamp") else pd.NaT,
            "updated_at"                    : datetime.datetime.strptime(item.get("updated_timestamp"), "%Y-%m-%dT%H:%M:%SZ") if item.get("updated_timestamp") else pd.NaT,
            "published_on"                  : datetime.datetime.strptime(item.get("cve", {}).get("published_date"), "%Y-%m-%dT%H:%M:%SZ") if item.get("cve", {}).get("published_date") else pd.NaT,
            "spotlight_published_at"        : datetime.datetime.strptime(item.get("cve", {}).get("spotlight_published_date"), "%Y-%m-%dT%H:%M:%SZ") if item.get("cve", {}).get("spotlight_published_date") else pd.NaT,
            "is_cisa_kev"                   : bool(item.get("cve", {}).get("cisa_info", {}).get("is_cisa_kev", False)),
            "is_suppressed"                 : bool(item.get("suppression_info", {}).get("is_suppressed", False)),
            "exploit_status"                : int(item.get("cve", {}).get("exploit_status", 0)),
            "has_exploit"                   : bool(int(item.get("cve", {}).get("exploit_status", 0)) >= 90),
            "has_patch"                     : bool(item.get("cve", {}).get("remediation_level") == 'O'),
            "exploitability_score"          : float(item.get("cve", {}).get("exploitability_score", 0)),
            "impact_score"                  : float(item.get("cve", {}).get("impact_score", 0)),
            "base_score"                    : float(item.get("cve", {}).get("base_score", 0)),
        }

    def vulnerabilities(self):
        logging.info('crowdstrike - vulnerabilities')
        query_filter = "cve.id:!['']+last_seen_within:'5'+status:['open','reopen']"
        cursor_restarted = False

        def _paginate():
            retrieved = 0
            after = None
            total = 1
            while retrieved <= total:
                total, after, returned, result = self.query_spotlight(aft=after, query_filter=query_filter)
                retrieved += returned
                df = pd.DataFrame([self._vulnerabilities(item) for item in result])
                self.collector.store_df('crowdstrike_vulnerabilities', df)
                df = pd.DataFrame([self._remediation(item, entity)
                    for item in result
                    for entity in item.get("remediation", {}).get("entities", [])
                ])
                self.collector.store_df('crowdstrike_vulnerabilities_remediation', df)

        try:
            _paginate()
        except SpotlightCursorExpiredError:
            if cursor_restarted:
                logging.error("Spotlight cursor expired on retry — giving up.")
                raise
            logging.warning(f"Spotlight cursor expired mid-pagination. Clearing accumulated data and restarting from scratch.")
            for tag in ('crowdstrike_vulnerabilities', 'crowdstrike_vulnerabilities_remediation'):
                self.collector.df[tag] = pd.DataFrame()
                self.collector.row_count[tag] = 0
            cursor_restarted = True
            _paginate()

        self.collector.write_df('crowdstrike_vulnerabilities')
        self.collector.write_df('crowdstrike_vulnerabilities_remediation')
        return self.collector.df.get('crowdstrike_vulnerabilities', pd.DataFrame())
        
    def query_spotlight(self, aft: str = None, query_filter: str = ''):
        """Retrieve a batch of Spotlight Vulnerability matches with connection retry and 429 backoff."""

        spotlight = SpotlightVulnerabilities(
            client_id=os.environ["FALCON_CLIENT_ID"],
            client_secret=os.environ["FALCON_SECRET"]
        )

        retry_wait = 0.5
        max_wait = 60
        max_rate_limit_retries = 5
        max_connect_retries = 2
        rate_limit_retries = 0
        connect_attempts = 0

        while True:
            try:
                all_results = spotlight.query_vulnerabilities_combined(
                    filter=query_filter,
                    after=aft,
                    sort="updated_timestamp|asc",
                    limit=400,
                    facet={"cve", "host_info", "remediation"}
                )
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.ChunkedEncodingError) as e:
                connect_attempts += 1
                if connect_attempts <= max_connect_retries:
                    logging.warning(f"Connection error (attempt {connect_attempts}/{max_connect_retries + 1}). Retrying in 5s: {e}")
                    time.sleep(5)
                    continue
                logging.error(f"Connection failed after {max_connect_retries + 1} attempts: {e}")
                raise

            stat = all_results["status_code"]

            if stat == 429:
                rate_limit_retries += 1
                if rate_limit_retries <= max_rate_limit_retries:
                    logging.warning(f"Rate limit met, retrying in {retry_wait:.2f}s (attempt {rate_limit_retries}/{max_rate_limit_retries}).")
                    time.sleep(retry_wait)
                    retry_wait = min(retry_wait * 2, max_wait)
                    continue
                logging.error(f"Spotlight rate limit retries exhausted after {max_rate_limit_retries} attempts.")
                raise Exception("Spotlight rate limit retries exhausted")

            if stat == 404:
                logging.warning("Spotlight cursor expired (404). Pagination cursor TTL exceeded.")
                raise SpotlightCursorExpiredError("Spotlight cursor expired")

            if stat != 200:
                logging.error(f"Failed to retrieve Spotlight Vulnerability matches. Status: {stat}")
                raise Exception(f"Spotlight API error: {stat}")

            return (
                all_results["body"]["meta"]["pagination"]["total"],
                all_results["body"]["meta"]["pagination"]["after"],
                len(all_results["body"]["resources"]),
                all_results["body"]["resources"]
            )

    def _zero_trust_assessment(self,item):
        return {
            "aid"                       : item.get("aid"),
            "cid"                       : item.get("cid"),
            "system_serial_number"      : item.get("system_serial_number"),
            "event_platform"            : item.get("event_platform"),
            "product_type_desc"         : item.get("product_type_desc"),
            "modified_time"             : datetime.datetime.strptime(item["modified_time"], "%Y-%m-%dT%H:%M:%SZ") if item.get("modified_time") else pd.NaT,
            "sensor_file_status"        : item.get("sensor_file_status"),
            "assessment_sensor_config"  : int(item.get("assessment",{}).get("sensor_config",0)),
            "assessment_overall"        : int(item.get("assessment",{}).get("overall",0)),
            "assessment_version"        : item.get("assessment",{}).get("version",0),
        }

    def _signals(self,item,signal_type,entity):
        return {
            "aid"            : item.get("aid"),
            "type"           : signal_type,
            "criteria"       : entity.get("criteria", ""),
            "group_name"     : entity.get("group_name", ""),
            "meets_criteria" : entity.get("meets_criteria", ""),
            "signal_id"      : entity.get("signal_id", ""),
            "signal_name"    : entity.get("signal_name", "")
        }

    def zero_trust_assessment(self):
        logging.info('crowdstrike - zero_trust_assessment')
        zta = ZeroTrustAssessment(
            client_id=os.environ["FALCON_CLIENT_ID"],
            client_secret=os.environ["FALCON_SECRET"]
        )
        for id_list in self.host_list:
            result = self._call_with_retry(zta.get_assessment, ids=id_list)
            if result["status_code"] != 200:
                logging.error(f"crowdstrike zero_trust_assessment: API returned {result['status_code']}")
                raise Exception(f"crowdstrike zero_trust_assessment API error: {result['status_code']}")
            response = result['body']['resources']
            logging.info(f"Retrieved {len(response)} ZTA records for batch of {len(id_list)} hosts")
            df = pd.DataFrame([self._zero_trust_assessment(item) for item in response])
            self.collector.store_df('crowdstrike_zero_trust_assessment', df)
            df = pd.DataFrame([self._signals(item, signal_type, entity)
                for item in response
                for signal_type in ["os_signals", "sensor_signals"]
                for entity in item.get("assessment_items", {}).get(signal_type, [])
            ])
            self.collector.store_df('crowdstrike_zero_trust_assessment_items', df)
        self.collector.write_df('crowdstrike_zero_trust_assessment')
        self.collector.write_df('crowdstrike_zero_trust_assessment_items')
        return self.collector.df.get('crowdstrike_zero_trust_assessment', pd.DataFrame())

if __name__ == '__main__':
    import sys
    load_dotenv()
    sys.path.append("../")
    sys.path.append("./")
    from collector import Collector
    C = Collector()
    S = Source(C)
