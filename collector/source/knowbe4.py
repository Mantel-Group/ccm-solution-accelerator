import requests
import os
import sys
import logging
import datetime
import pandas as pd
import time
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s'
)

class Source:
    def __init__(self,C):
        self.collector = C
        self.last_request_time = 0
        self.request_delay = 0.25  # 4 requests per second = 0.25 seconds between requests

        # -- check the environment variables that will define if this plugin runs
        if C.env({
                'KNOWBE4_TOKEN'     : None,
                'KNOWBE4_ENDPOINT'  : "https://us.api.knowbe4.com"
            }):

            self.headers = {
                "Authorization" : f"Bearer {os.environ['KNOWBE4_TOKEN']}",
                "Accept"        : "application/json",
            }

            if self.enrollments().empty:
                self.collector.write_blank('knowbe4_enrollments'                       , self._enrollments({}))

            # Extract PSTs
            pst_ids = self.psts()
            if not pst_ids:
                self.collector.write_blank('knowbe4_psts', self._psts({}))

            # Extract PST Recipients
            if pst_ids:
                recipient_df = self.pst_recipients(pst_ids)
                if recipient_df.empty:
                    self.collector.write_blank('knowbe4_pst_recipients', self._pst_recipients({}, ''))
            else:
                self.collector.write_blank('knowbe4_pst_recipients', self._pst_recipients({}, ''))

        else:
            self.collector.write_blank('knowbe4_enrollments'                       , self._enrollments({}))
            self.collector.write_blank('knowbe4_psts', self._psts({}))
            self.collector.write_blank('knowbe4_pst_recipients', self._pst_recipients({}, ''))

    def _make_request(self, url, max_retries=5):
        """
        Make API request with rate limiting and exponential backoff

        KnowBe4 API Limits:
        - 4 requests per second
        - 50 requests per minute (burst limit)
        - 2,000 requests per day + licensed users
        """
        # Proactive rate limiting: ensure minimum delay between requests
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.request_delay:
            sleep_time = self.request_delay - time_since_last_request
            time.sleep(sleep_time)

        retry_delay = 15  # Start with 15 seconds for 429 errors (burst limit recovery)

        for attempt in range(max_retries):
            try:
                self.last_request_time = time.time()
                req = requests.get(url, headers=self.headers, timeout=30)
                req.raise_for_status()
                return req
            except requests.exceptions.HTTPError as err:
                if err.response.status_code == 429:
                    if attempt < max_retries - 1:
                        logging.warning(f"Rate limit hit (429). Retrying in {retry_delay} seconds... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(retry_delay)
                        retry_delay = min(retry_delay * 2, 300)  # Exponential backoff, max 5 minutes
                    else:
                        logging.error(f"Rate limit exceeded after {max_retries} attempts for URL: {url}")
                        raise
                else:
                    raise

        return None

    def _enrollments(self,item):
        return {
            "campaign_name"         : item.get("campaign_name"),
            "completion_date"       : datetime.datetime.strptime(item["completion_date"], "%Y-%m-%dT%H:%M:%S.000Z") if item.get("completion_date") else pd.NaT,
            "content_type"          : item.get("content_type"),
            "enrollment_date"       : datetime.datetime.strptime(item["enrollment_date"], "%Y-%m-%dT%H:%M:%S.000Z") if item.get("enrollment_date") else pd.NaT,
            "enrollment_id"         : int(item["enrollment_id"]) if item.get("enrollment_id") not in [None, ""] else None,
            "module_name"           : item.get("module_name"),
            "policy_acknowledged"   : item.get("policy_acknowledged",False),
            "start_date"            : datetime.datetime.strptime(item["start_date"], "%Y-%m-%dT%H:%M:%S.000Z") if item.get("start_date") else pd.NaT,
            "status"                : item.get("status"),
            "time_spent"            : item.get("time_spent"),
            "email"                 : item.get("user",{}).get("email"),
            "first_name"            : item.get("user",{}).get("first_name"),
            "last_name"             : item.get("user",{}).get("last_name"),
            "id"                    : item.get("user",{}).get("id"),
        }

    def _psts(self, item):
        return {
            "campaign_id": item.get("campaign_id"),
            "pst_id": item.get("pst_id"),
            "status": item.get("status"),
            "name": item.get("name"),
            "groups": str(item.get("groups")) if item.get("groups") else None,
            "phish_prone_percentage": float(item["phish_prone_percentage"]) if item.get("phish_prone_percentage") not in [None, ""] else None,
            "started_at": datetime.datetime.strptime(item["started_at"], "%Y-%m-%dT%H:%M:%S.000Z") if item.get("started_at") else pd.NaT,
            "duration": item.get("duration"),
            "categories": str(item.get("categories")) if item.get("categories") else None,
            "template_id": item.get("template_id"),
            "landing_page_id": item.get("landing_page_id"),
            "scheduled_count": int(item["scheduled_count"]) if item.get("scheduled_count") not in [None, ""] else None,
            "delivered_count": int(item["delivered_count"]) if item.get("delivered_count") not in [None, ""] else None,
            "opened_count": int(item["opened_count"]) if item.get("opened_count") not in [None, ""] else None,
            "clicked_count": int(item["clicked_count"]) if item.get("clicked_count") not in [None, ""] else None,
            "replied_count": int(item["replied_count"]) if item.get("replied_count") not in [None, ""] else None,
            "attachment_open_count": int(item["attachment_open_count"]) if item.get("attachment_open_count") not in [None, ""] else None,
            "macro_enabled_count": int(item["macro_enabled_count"]) if item.get("macro_enabled_count") not in [None, ""] else None,
            "data_entered_count": int(item["data_entered_count"]) if item.get("data_entered_count") not in [None, ""] else None,
            "qr_code_scanned_count": int(item["qr_code_scanned_count"]) if item.get("qr_code_scanned_count") not in [None, ""] else None,
            "reported_count": int(item["reported_count"]) if item.get("reported_count") not in [None, ""] else None,
            "bounced_count": int(item["bounced_count"]) if item.get("bounced_count") not in [None, ""] else None,
        }

    def _pst_recipients(self, item, pst_id):
        return {
            "pst_id": pst_id,
            "recipient_id": item.get("recipient_id"),
            "user_id": item.get("user",{}).get("id"),
            "user_first_name": item.get("user",{}).get("first_name"),
            "user_last_name": item.get("user",{}).get("last_name"),
            "user_email": item.get("user",{}).get("email"),
            "template_name": item.get("template",{}).get("name"),
            "scheduled_at": datetime.datetime.strptime(item["scheduled_at"], "%Y-%m-%dT%H:%M:%S.000Z") if item.get("scheduled_at") else pd.NaT,
            "delivered_at": datetime.datetime.strptime(item["delivered_at"], "%Y-%m-%dT%H:%M:%S.000Z") if item.get("delivered_at") else pd.NaT,
            "opened_at": datetime.datetime.strptime(item["opened_at"], "%Y-%m-%dT%H:%M:%S.000Z") if item.get("opened_at") else pd.NaT,
            "clicked_at": datetime.datetime.strptime(item["clicked_at"], "%Y-%m-%dT%H:%M:%S.000Z") if item.get("clicked_at") else pd.NaT,
            "replied_at": datetime.datetime.strptime(item["replied_at"], "%Y-%m-%dT%H:%M:%S.000Z") if item.get("replied_at") else pd.NaT,
            "attachment_opened_at": datetime.datetime.strptime(item["attachment_opened_at"], "%Y-%m-%dT%H:%M:%S.000Z") if item.get("attachment_opened_at") else pd.NaT,
            "macro_enabled_at": datetime.datetime.strptime(item["macro_enabled_at"], "%Y-%m-%dT%H:%M:%S.000Z") if item.get("macro_enabled_at") else pd.NaT,
            "data_entered_at": datetime.datetime.strptime(item["data_entered_at"], "%Y-%m-%dT%H:%M:%S.000Z") if item.get("data_entered_at") else pd.NaT,
            "qr_code_scanned_at": datetime.datetime.strptime(item["qr_code_scanned_at"], "%Y-%m-%dT%H:%M:%S.000Z") if item.get("qr_code_scanned_at") else pd.NaT,
            "reported_at": datetime.datetime.strptime(item["reported_at"], "%Y-%m-%dT%H:%M:%S.000Z") if item.get("reported_at") else pd.NaT,
            "bounced_at": datetime.datetime.strptime(item["bounced_at"], "%Y-%m-%dT%H:%M:%S.000Z") if item.get("bounced_at") else pd.NaT,
            "ip": item.get("ip"),
            "ip_location": item.get("ip_location"),
            "browser": item.get("browser"),
            "browser_version": item.get("browser_version"),
            "os": item.get("os"),
        }
    
    def enrollments(self):
        page = 1
        while True:
            try:
                url = f"{os.environ['KNOWBE4_ENDPOINT']}/v1/training/enrollments?page={page}"
                req = self._make_request(url)
                if req is None:
                    break
            except requests.exceptions.HTTPError as err:
                logging.critical(f"Something went wrong with knowbe4 : {err}")
                break

            result = req.json()
            page += 1
            df = pd.DataFrame([ self._enrollments(item) for item in result ])
            self.collector.store_df('knowbe4_enrollments', df)

            if len(result) == 0:
                break

        self.collector.write_df('knowbe4_enrollments')
        return self.collector.df.get('knowbe4_enrollments',pd.DataFrame())

    def psts(self):
        page = 1
        pst_ids = []

        while True:
            try:
                url = f"{os.environ['KNOWBE4_ENDPOINT']}/v1/phishing/security_tests?page={page}"
                req = self._make_request(url)
                if req is None:
                    break
            except requests.exceptions.HTTPError as err:
                logging.critical(f"Error fetching KnowBe4 PSTs: {err}")
                break

            result = req.json()
            page += 1

            for item in result:
                if item.get("pst_id"):
                    pst_ids.append(item["pst_id"])

            df = pd.DataFrame([self._psts(item) for item in result])
            self.collector.store_df('knowbe4_psts', df)

            if len(result) == 0:
                break

        self.collector.write_df('knowbe4_psts')
        return pst_ids

    def pst_recipients(self, pst_ids):
        if not pst_ids:
            logging.info("No PST IDs available for recipient extraction")
            return pd.DataFrame()

        logging.info(f"Extracting recipients for {len(pst_ids)} PSTs")

        for pst_id in pst_ids:
            page = 1

            while True:
                try:
                    url = f"{os.environ['KNOWBE4_ENDPOINT']}/v1/phishing/security_tests/{pst_id}/recipients?page={page}"
                    req = self._make_request(url)
                    if req is None:
                        break
                except requests.exceptions.HTTPError as err:
                    logging.error(f"Error fetching recipients for PST {pst_id}: {err}")
                    break

                result = req.json()
                page += 1

                if result:
                    df = pd.DataFrame([self._pst_recipients(item, pst_id) for item in result])
                    self.collector.store_df('knowbe4_pst_recipients', df)

                if len(result) == 0:
                    break

            logging.info(f"Completed recipient extraction for PST {pst_id}")

        self.collector.write_df('knowbe4_pst_recipients')
        return self.collector.df.get('knowbe4_pst_recipients', pd.DataFrame())

# == we create the __main__ bit to allow the plugin to be manually run when needed.
if __name__ == '__main__':
    import sys
    load_dotenv()
    sys.path.append("../")
    sys.path.append("./")
    from collector import Collector
    C = Collector()
    S = Source(C)