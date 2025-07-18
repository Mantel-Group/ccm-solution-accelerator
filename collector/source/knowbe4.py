import requests
import os
import sys
import logging
import datetime
import pandas as pd
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s'
)

class Source:
    def __init__(self,C):
        self.collector = C
        # -- check the environment variables that will define if this plugin runs
        if C.env({
                'KNOWBE4_TOKEN'     : None,
                'KNOWBE4_ENDPOINT'  : "https://us.api.knowbe4.com/v1/training/enrollments"
            }):
        
            self.headers = {
                "Authorization" : f"Bearer {os.environ['KNOWBE4_TOKEN']}",
                "Accept"        : "application/json",
            }

            if self.enrollments().empty:
                self.collector.write_blank('knowbe4_enrollments'                       , self._enrollments({}))

        else:
            self.collector.write_blank('knowbe4_enrollments'                       , self._enrollments({}))

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
    
    def enrollments(self):
        page = 1
        while True:
            try:
                req = requests.get(
                        f"{os.environ['KNOWBE4_ENDPOINT']}?page={page}",
                        headers = self.headers,
                        timeout=30
                    )
                req.raise_for_status()
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

# == we create the __main__ bit to allow the plugin to be manually run when needed.
if __name__ == '__main__':
    import sys
    load_dotenv()
    sys.path.append("../")
    sys.path.append("./")
    from collector import Collector
    C = Collector()
    S = Source(C)