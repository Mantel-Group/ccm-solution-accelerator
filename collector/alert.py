import os
import sys
import requests
import logging
import json
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('alert.log')
    ]
)

class Alert():
    def __init__(self):
        load_dotenv('../.env')
        load_dotenv('.env')
        self.alert_fatique = []

    def send(self,msg,severity=None):

        # == build the actual message we will send.
        severity_icons = {
            'ERROR'   : ':x:',
            'INFO'    : ':information_source:',
            'SUCCESS' : ':white_check_mark:',
            'WARNING' : ':warning:'
        }
        icon = severity_icons.get(severity, '')
        message = f"{icon} - {os.environ.get('_TENANT','default')} - {msg}" if icon else msg

        if not msg in self.alert_fatique:
            self.alert_fatique.append(msg)
            if os.environ.get('ALERT_SLACK_CHANNEL','') != '' and  os.environ.get('ALERT_SLACK_TOKEN','') != '':
                # == send a slack message
                req = requests.post(
                    "https://slack.com/api/chat.postMessage",
                    headers = { 'Authorization': f"Bearer {os.environ['ALERT_SLACK_TOKEN']}" },
                    data = { 'channel' : os.environ['ALERT_SLACK_CHANNEL'] , 'type' : 'mrkdwn', 'text' : message},
                )
        
                if req.status_code == 200:
                    print(" - success")
                    logging.info(f"Sent a slack alert : {msg}")
                else:
                    logging.error(f"Unable to send a slack alert : {req.status_code} - {msg}")
            
            if os.environ.get('ALERT_SLACK_WEBHOOK','') != '':
                try:
                    x = requests.post(os.environ['ALERT_SLACK_WEBHOOK'],data=json.dumps({ 'type': 'mrkdwn', 'text' : message }).encode('utf-8'),headers = {   
                        'Content-Type': 'application/json'})
                    logging.info(f"Sent a slack alert : {msg}")
                except Exception as e:
                    logging.error(f"Unable to send a slack alert : {x.status_code} - {msg}")
            
if __name__ == '__main__':
    A = Alert()
    if len(sys.argv) == 2:
        A.send(sys.argv[1])
    else:
        A.send("Hello World.")