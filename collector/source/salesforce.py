from simple_salesforce import Salesforce
from dotenv import load_dotenv
import os
import sys
import logging
import pandas as pd
import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
)

class Source:
    def __init__(self,C):
        self.collector = C
        # -- check the environment variables that will define if this plugin runs
        if C.env({
                "SALESFORCE_USERNAME"       : None,
                "SALESFORCE_PASSWORD"       : None,
                "SALESFORCE_TOKEN"          : None,
                "SALESFORCE_ENDPOINT"       : None,
            }):
            self.sf = Salesforce(
                instance=os.environ['SALESFORCE_ENDPOINT'],
                username=os.environ['SALESFORCE_USERNAME'],
                password=os.environ['SALESFORCE_PASSWORD'],
                security_token=os.environ['SALESFORCE_TOKEN']
            )
        else:
            self.sf = None

        self.salesforce('salesforce_fixed_asset__c','select id, project_resource__c, status__c, type__c, serial_number__c, model__c FROM fixed_asset__c',{ 'Id' : 'text', 'Project_Resource__c' : 'text', 'Status__c' : 'text', 'Type__c' : 'text', 'Serial_Number__c' : 'text', 'Model__c' : 'text'})
        self.salesforce('salesforce_krow__location__c','select id,name from krow__location__c', { 'Id' : 'text','Name' : 'text'})
        self.salesforce('salesforce_krow__project_resources__c','select id,name,user_email__c,employment_end_date__c,legal_name__c,domain__c,employment_start_date__c,krow__team__c,krow__active__c,krow__location__c from krow__project_resources__c',{"Id": "text","Name": "text","User_Email__c": "text","Employment_End_Date__c": "date","Legal_Name__c": "text","Domain__c": "text","Employment_Start_Date__c": "date","Krow__Team__c": "text","Krow__Active__c": "Boolean","Krow__Location__c": "text"})
        self.salesforce('salesforce_domain__c','select id,name,active__c from domain__c',{ 'Id' : 'text','Name' : 'text','Active__c' : 'boolean'})
        self.salesforce('salesforce_krow__team__c','select id,name from krow__team__c',{ 'Id' : 'text','Name' : 'text'})
        
    def salesforce_empty(self,table,schema):
        logging.info(f"Writing an empty salesforce table - {table}")
        y = {}
        for i, dtype in schema.items():
            key = i.lower()
            value = None
            if dtype == 'text':
                y[key] = value if value is not None else ''
            elif dtype == 'boolean':
                y[key] = value if value is not None else False
            elif dtype == 'date':
                y[key] = datetime.datetime.strptime(value, "%Y-%m-%d") if value else None
        df = pd.DataFrame([ y ])
        print(df)
        self.collector.store_df(table, df)
        self.collector.write_df(table)

    def salesforce(self,table,sql,schema):
        logging.info(f"Salesforce - {table}")
        if not self.sf:
            self.salesforce_empty(table,schema)
            return
        
        try:
            data = dict(self.sf.query_all(sql))['records']
            logging.info(f" - Retrieved {len(data)} records")
        except Exception as e:
            logging.error(f" - Error retrieving Salesforce data - {e}")
            data = {}
       
        # parse the retrieved data
        new = []
        for x in data:
            y = {}
            for i, dtype in schema.items():
                key = i.lower()
                value = x.get(i)
                if dtype == 'text':
                    y[key] = value if value is not None else ''
                elif dtype == 'boolean':
                    y[key] = value if value is not None else False
                elif dtype == 'date':
                    y[key] = datetime.datetime.strptime(value, "%Y-%m-%d") if value else None
            new.append(y)
        df = pd.DataFrame(new)
        if df.empty:
            df = self.salesforce_empty(table,schema)
        else:
            self.collector.store_df(table, df)
            self.collector.write_df(table)

# == we create the __main__ bit to allow the plugin to be manually run when needed.
if __name__ == '__main__':
    import sys
    sys.path.append("../")
    sys.path.append("./")
    from collector import Collector
    load_dotenv()
    C = Collector()
    S = Source(C)