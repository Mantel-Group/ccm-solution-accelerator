# VERY IMPORTANT - do not call this file tenable.py - it clashes with internal namings, and won't work

from tenable.io import TenableIO
import os
import sys
import logging
import pandas as pd
import datetime
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s'
)

class Source:
    def __init__(self,C):
        self.collector = C

        if C.env({
            'TENABLE_ACCESS_KEY' : None,
            'TENABLE_SECRET_KEY' : None,
        }):
            self.tio = TenableIO(
                access_key=os.environ['TENABLE_ACCESS_KEY'],
                secret_key=os.environ['TENABLE_SECRET_KEY']
            )

            if self.assets().empty:
                self.collector.write_blank('tenable_assets'         , self._assets({})          )
            if self.vulnerabilities().empty:
                self.collector.write_blank('tenable_vulnerabilities', self._vulnerabilities({}) )
            #self.findings()
            #self.was()
        else:
            self.collector.write_blank('tenable_assets'         , self._assets({})          )
            self.collector.write_blank('tenable_vulnerabilities', self._vulnerabilities({}) )

    # def findings(self):
    #     flatten = []
    #     for d in self.tio.exports.compliance():
    #         flatten.append(d)
    #         print(d)
    #     self.collector.store('tenable_findings',flatten)

    def _assets(self,item):
        return {
            "id"                            : item.get("id"),
            "has_agent"                     : item.get("has_agent",False) == True,
            "has_plugin_results"            : item.get("has_plugin_results",False) == True,
            "created_at"                    : datetime.datetime.strptime(item["created_at"].split('.')[0], "%Y-%m-%dT%H:%M:%S") if item.get("created_at") else pd.NaT,
            "terminated_at"                 : datetime.datetime.strptime(item["terminated_at"].split('.')[0], "%Y-%m-%dT%H:%M:%S") if item.get("terminated_at") else pd.NaT,
            "terminated_by"                 : item.get("terminated_by"),
            "updated_at"                    : datetime.datetime.strptime(item["updated_at"].split('.')[0], "%Y-%m-%dT%H:%M:%S") if item.get("updated_at") else pd.NaT,
            "deleted_at"                    : datetime.datetime.strptime(item["deleted_at"].split('.')[0], "%Y-%m-%dT%H:%M:%S") if item.get("deleted_at") else pd.NaT,
            "deleted_by"                    : item.get("deleted_by"),
            "first_seen"                    : datetime.datetime.strptime(item["first_seen"].split('.')[0], "%Y-%m-%dT%H:%M:%S") if item.get("first_seen") else pd.NaT,
            "last_seen"                     : datetime.datetime.strptime(item["last_seen"].split('.')[0], "%Y-%m-%dT%H:%M:%S") if item.get("last_seen") else pd.NaT,
            "first_scan_time"               : datetime.datetime.strptime(item["first_scan_time"].split('.')[0], "%Y-%m-%dT%H:%M:%S") if item.get("first_scan_time") else pd.NaT,
            "last_scan_time"                : datetime.datetime.strptime(item["last_scan_time"].split('.')[0], "%Y-%m-%dT%H:%M:%S") if item.get("last_scan_time") else pd.NaT,
            "last_authenticated_scan_date"  : datetime.datetime.strptime(item["last_authenticated_scan_date"].split('.')[0], "%Y-%m-%dT%H:%M:%S") if item.get("last_authenticated_scan_date") else pd.NaT,
            "last_licensed_scan_date"       : datetime.datetime.strptime(item["last_licensed_scan_date"].split('.')[0], "%Y-%m-%dT%H:%M:%S") if item.get("last_licensed_scan_date") else pd.NaT,
            "last_scan_id"                  : item.get("last_scan_id"),
            "last_schedule_id"              : item.get("last_schedule_id"),
            "azure_vm_id"                   : item.get("azure_vm_id"),
            "azure_resource_id"             : item.get("azure_resource_id"),
            "gcp_project_id"                : item.get("gcp_project_id"),
            "gcp_zone"                      : item.get("gcp_zone"),
            "gcp_instance_id"               : item.get("gcp_instance_id"),
            "aws_ec2_instance_ami_id"       : item.get("aws_ec2_instance_ami_id"),
            "aws_ec2_instance_id"           : item.get("aws_ec2_instance_id"),
            "agent_uuid"                    : item.get("agent_uuid"),
            "bios_uuid"                     : item.get("bios_uuid"),
            "network_id"                    : item.get("network_id"),
            "network_name"                  : item.get("network_name"),
            "aws_owner_id"                  : item.get("aws_owner_id"),
            "aws_availability_zone"         : item.get("aws_availability_zone"),
            "aws_region"                    : item.get("aws_region"),
            "aws_vpc_id"                    : item.get("aws_vpc_id"),
            "aws_ec2_instance_group_name"   : item.get("aws_ec2_instance_group_name"),
            "aws_ec2_instance_state_name"   : item.get("aws_ec2_instance_state_name"),
            "aws_ec2_instance_type"         : item.get("aws_ec2_instance_type"),
            "aws_subnet_id"                 : item.get("aws_subnet_id"),
            "aws_ec2_product_code"          : item.get("aws_ec2_product_code"),
            "aws_ec2_name"                  : item.get("aws_ec2_name"),
            "mcafee_epo_guid"               : item.get("mcafee_epo_guid"),
            "mcafee_epo_agent_guid"         : item.get("mcafee_epo_agent_guid"),
            "servicenow_sysid"              : item.get("servicenow_sysid"),
            "bigfix_asset_id"               : item.get("bigfix_asset_id"),
            "ipv4s"                         : item.get("ipv4s", [None])[0] if item.get("ipv4s") else None,
            "ipv6s"                         : item.get("ipv6s", [None])[0] if item.get("ipv6s") else None,
            "fqdns"                         : item.get("fqdns", [None])[0] if item.get("fqdns") else None,
            "mac_addresses"                 : item.get("mac_addresses", [None])[0] if item.get("mac_addresses") else None,
            "netbios_names"                 : item.get("netbios_names", [None])[0] if item.get("netbios_names") else None,
            "operating_systems"             : item.get("operating_systems", [None])[0] if item.get("operating_systems") else None,
            "system_types"                  : item.get("system_types", [None])[0] if item.get("system_types") else None,
            "hostnames"                     : item.get("hostnames", [None])[0] if item.get("hostnames") else None,
            "source_name"                   : item.get("sources", [{}])[0].get("name") if item.get("sources") else None,
            "source_first_seen"             : datetime.datetime.strptime(item["sources"][0].get("first_seen", "").split('.')[0], "%Y-%m-%dT%H:%M:%S") if item.get("sources",[{}])[0].get("first_seen") else pd.NaT,
            "source_last_seen"              : datetime.datetime.strptime(item["sources"][0].get("last_seen", "").split('.')[0], "%Y-%m-%dT%H:%M:%S") if item.get("sources",[{}])[0].get("last_seen") else pd.NaT,
            "serial_number"                 : item.get("serial_number"),
            "acr_score"                     : float(item.get("acr_score") or 0),
            "exposure_score"                : float(item.get("exposure_score") or 0),
            "rating_acr_score"              : item.get("ratings", {}).get("acr", {}).get("score"),
            "rating_aes_score"              : item.get("ratings", {}).get("aes", {}).get("score")
        }
    
    def assets(self):
        result = []
        if self.tio:
            result = list(self.tio.exports.assets())
        if len(result) == 0:
            return pd.DataFrame()
        else:
            df = pd.DataFrame([ self._assets(item) for item in result])
            self.collector.store_df('tenable_assets',df)
            self.collector.write_df('tenable_assets')
            return df


        #     # "agent_names": item["agent_names"],  # empty list
        #     # "installed_software": item["installed_software"],  # empty list
        #     # "ssh_fingerprints": item["ssh_fingerprints"],  # empty list
        #     # "qualys_asset_ids": item["qualys_asset_ids"],  # empty list
        #     # "qualys_host_ids": item["qualys_host_ids"],  # empty list
        #     # "manufacturer_tpm_ids": item["manufacturer_tpm_ids"],  # empty list
        #     # "symantec_ep_hardware_keys": item["symantec_ep_hardware_keys"],  # empty list
        #     # "open_ports": item["open_ports"],  # empty list
        
        #     "tag_key": item["tags"][0]["key"] if item["tags"] else None,
        #     "tag_value": item["tags"][0]["value"] if item["tags"] else None,
        #     "tag_added_at": datetime.datetime.strptime(item["tags"][0]["added_at"].split('.')[0], "%Y-%m-%dT%H:%M:%S") if item["tags"] and item["tags"][0].get("added_at") else None,
        
    # def was(self):
    #     # -- Retrieve the data and flatten it
    #     flatten = []
    #     for d in self.tio.was.export():
    #         flatten.append(d)
    #     self.collector.store('tenable_was',flatten)

    def _vulnerabilities(self, item):
        return {
            "id"                           : item.get("id"),
            "output"                       : item.get("output"),
            #"port"                         : json.dumps(item.get("port",{})),
            "protocol"                     : item.get("protocol"),
            "severity"                     : item.get("severity"),
            "state"                        : item.get("state"),
            "first_found"                  : datetime.datetime.strptime(item["first_found"].rstrip('Z').split('.')[0], "%Y-%m-%dT%H:%M:%S") if item.get("first_found") else pd.NaT,
            "last_found"                   : datetime.datetime.strptime(item["last_found"].rstrip('Z').split('.')[0] , "%Y-%m-%dT%H:%M:%S") if item.get("last_found") else pd.NaT,

            # Plugin info
            "plugin_id"                    : item.get("plugin", {}).get("id"),
            "plugin_name"                  : item.get("plugin", {}).get("name"),
            "plugin_family"                : item.get("plugin", {}).get("family"),
            "plugin_modification_date"     : datetime.datetime.strptime(item["plugin"]["modification_date"], "%Y-%m-%dT%H:%M:%SZ") if item.get("plugin", {}).get("modification_date") else pd.NaT,
            "plugin_published_date"        : datetime.datetime.strptime(item["plugin"]["published_date"], "%Y-%m-%dT%H:%M:%SZ") if item.get("plugin", {}).get("published_date") else pd.NaT,
            "plugin_type"                  : item.get("plugin", {}).get("type"),
            "plugin_description"           : item.get("plugin", {}).get("description"),
            "plugin_solution"              : item.get("plugin", {}).get("solution"),
            "plugin_synopsis"              : item.get("plugin", {}).get("synopsis"),
            "plugin_risk_factor"           : item.get("plugin", {}).get("risk_factor"),
            "plugin_see_also"              : item.get("plugin", {}).get("see_also", []),
            "plugin_cpe"                   : json.dumps(item.get("plugin", {}).get("cpe", [])),
            "plugin_xrefs"                 : json.dumps(item.get("plugin", {}).get("xrefs", [None])),

            # CVSS v2
            "cvss_v2_base_score"           : item.get("plugin", {}).get("cvss", {}).get("base_score"),
            "cvss_v2_vector"               : item.get("plugin", {}).get("cvss", {}).get("vector"),
            "cvss_v2_temporal_score"       : item.get("plugin", {}).get("cvss", {}).get("temporal_score"),
            "cvss_v2_temporal_vector"      : item.get("plugin", {}).get("cvss", {}).get("temporal_vector"),

            # CVSS v3
            "cvss_v3_base_score"           : item.get("plugin", {}).get("cvss3", {}).get("base_score"),
            "cvss_v3_vector"               : item.get("plugin", {}).get("cvss3", {}).get("vector"),
            "cvss_v3_temporal_score"       : item.get("plugin", {}).get("cvss3", {}).get("temporal_score"),
            "cvss_v3_temporal_vector"      : item.get("plugin", {}).get("cvss3", {}).get("temporal_vector"),

            # Exploit data
            "has_patch"                    : item.get("plugin", {}).get("has_patch",False),
            "has_exploit"                  : item.get("plugin", {}).get("exploit_available",False),
            "exploit_available"            : item.get("plugin", {}).get("exploit", {}).get("available"),
            "exploit_frameworks"           : item.get("plugin", {}).get("exploit", {}).get("frameworks", [ None])[0],

            # Asset info
            "asset_uuid"                   : item.get("asset", {}).get("uuid"),
            "asset_hostname"               : item.get("asset", {}).get("hostname"),
            "asset_ipv4"                   : item.get("asset", {}).get("ipv4"),
            "asset_ipv6"                   : item.get("asset", {}).get("ipv6"),
            "asset_mac_address"            : item.get("asset", {}).get("mac_address"),
            "asset_operating_system"       : item.get("asset", {}).get("operating_system",[ None]) [0],
        }

    def vulnerabilities(self):
        result = [{}]
        if self.tio:
            result = list(self.tio.exports.vulns())
        if len(result) == 0:
            return pd.DataFrame()
        else:
            df = pd.DataFrame([ self._vulnerabilities(item) for item in result])
            self.collector.store_df('tenable_vulnerabilities',df)
            self.collector.write_df('tenable_vulnerabilities')
            return df

# == we create the __main__ bit to allow the plugin to be manually run when needed.
if __name__ == '__main__':
    import sys
    sys.path.append("../")
    sys.path.append("./")
    from collector import Collector
    C = Collector()
    S = Source(C)