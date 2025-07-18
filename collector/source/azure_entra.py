import requests
import os
import logging
from dotenv import load_dotenv
import sys
import pandas as pd
from datetime import datetime, timedelta, timezone

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s'
)

class Source:
    def __init__(self,C):
        self.collector = C

        if C.env({
            'AZURE_TENANT_ID' : None,
            'AZURE_CLIENT_ID' : None,
            'AZURE_CLIENT_SECRET' : None}):

            if self.users().empty:
                self.collector.write_blank('azure_entra_users', self._users({}))
            if self.signin().empty:
                self.collector.write_blank('azure_entra_users_signin', self._signin({}))
            if self.audit_logs().empty:
                self.collector.write_blank('azure_audit_logs', self._audit_logs({}))
        else:
            self.collector.write_blank('azure_entra_users', self._users({}))
            self.collector.write_blank('azure_entra_users_signin', self._signin({}))
            self.collector.write_blank('azure_audit_logs', self._audit_logs({}))

    def _users(self,item):
        return {
            "id"                             : item.get("id"),
            "display_name"                   : item.get("displayName"),
            "given_name"                     : item.get("givenName"),
            "surname"                        : item.get("surname"),
            "user_principal_name"            : item.get("userPrincipalName"),
            "mail"                           : item.get("mail"),
            "job_title"                      : item.get("jobTitle"),
            "department"                     : item.get("department"),
            "mobile_phone"                   : item.get("mobilePhone"),
            "business_phones"                : str(item.get("businessPhones")),
            "office_location"                : item.get("officeLocation"),
            "preferred_language"             : item.get("preferredLanguage"),
            "account_enabled"                : bool(item.get("accountEnabled")),
            "user_type"                      : item.get("userType"),
            "created_date_time"              : datetime.strptime(item.get("createdDateTime"), '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc) if item.get("createdDateTime") else pd.NaT,
            "last_password_change_date_time" : datetime.strptime(item.get("lastPasswordChangeDateTime"), '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc) if item.get("lastPasswordChangeDateTime") else pd.NaT,
        }
    
    def users(self):
        data = self._paginate('https://graph.microsoft.com/v1.0/users?$select=id,displayName,givenName,surname,userPrincipalName,mail,jobTitle,department,mobilePhone,businessPhones,officeLocation,preferredLanguage,accountEnabled,userType,createdDateTime,lastPasswordChangeDateTime')
        if data:
            df = pd.DataFrame([self._users(item) for item in data ])
            self.collector.store_df('azure_entra_users', df)
            self.collector.write_df('azure_entra_users')
            return df
        else:
            return pd.DataFrame()

    def _signin(self,item):
        return {
            "user_principal_name" : item.get("userPrincipalName"),
            "created_date_time"   : datetime.strptime(item.get("createdDateTime"), '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc) if item.get("createdDateTime") else pd.NaT,
        }

    def signin(self,days = 180):
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        formatted_date = cutoff_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        data = self._paginate(f'https://graph.microsoft.com/v1.0/auditLogs/signIns?$select=userPrincipalName,createdDateTime&$filter=createdDateTime ge {formatted_date}')
        if data:
            df = pd.DataFrame([self._signin(item) for item in data ])
            self.collector.store_df('azure_entra_users_signin', df)
            self.collector.write_df('azure_entra_users_signin')
            return df
        else:
            return pd.DataFrame()

    def _audit_logs(self,item):
        return {
            "id"                    : item.get("id"),
            "activity_display_name" : item.get("activityDisplayName"),
            "activity_date_time"    : datetime.strptime(item.get("activityDateTime").split('.')[0].replace('Z',''), '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc) if item.get("activityDateTime") else pd.NaT,
            "user_principal_name"   : item.get("targetResources",[{}])[0].get("userPrincipalName"),
            "initiated_by"          : item.get("initiatedBy",{}).get("user",{}).get("userPrincipalName") if item.get("initiatedBy",{}).get("user") != None else item.get("initiatedBy",{}).get("app",{}).get("displayName") 
        }

    def audit_logs(self):
        data = self._paginate(f"https://graph.microsoft.com/v1.0/auditLogs/directoryAudits?$select=activityDateTime,activityDisplayName,initiatedBy,targetResources")
        if data:
            df = pd.DataFrame([self._audit_logs(item) for item in data ])
            self.collector.store_df('azure_audit_logs', df)
            self.collector.write_df('azure_audit_logs')
            return df
        else:
            return pd.DataFrame()
            
    def _authenticate(self,graph_url):
        s = requests.Session()
        auth_url = f"https://login.microsoftonline.com/{os.environ['AZURE_TENANT_ID']}/oauth2/v2.0/token"
        auth_data = {
            "grant_type": "client_credentials",
            "client_id": os.environ['AZURE_CLIENT_ID'],
            "client_secret": os.environ['AZURE_CLIENT_SECRET'],
            "scope": f"{graph_url}/.default",
        }
        auth_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "cache-control": "no-cache",
        }
        res = s.post(auth_url, data=auth_data, headers=auth_headers)

        # Auth failed, raise exception with the response
        if res.status_code != 200:
            logging.error(f"{res.status_code} - {res.json().get("error_description")}")
            return None

        access_token = res.json().get("access_token")
        s.headers = {"Authorization": f"Bearer {access_token}", "cache-control": "no-cache"}
        return s

    def _paginate(self,graph_url,auth_url = 'https://graph.microsoft.com'):
        logging.info(f"=> {graph_url}")
        session = self._authenticate(auth_url)
        if session:
            data = []
            while True:
                ret = session.get(graph_url)
                z = ret.json()
                data += z.get('value',[])
                if z.get('@odata.nextLink'):
                    graph_url = z.get('@odata.nextLink')
                else:
                    break

            logging.info(f" - {len(data)} records")
            return data
        else:
            return None

if __name__ == '__main__':
    load_dotenv()
    import sys
    sys.path.append("../")
    sys.path.append("./")
    from collector import Collector
    C = Collector()
    S = Source(C)