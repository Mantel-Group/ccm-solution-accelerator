import requests
import logging
import sys
import os
from dotenv import load_dotenv
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s'
)

class Source:
    def __init__(self,C):
        self.collector = C
        # -- check the environment variables that will define if this plugin runs
        if C.env({
                'DOMAINS'     : None
            }):

            self.domain_list = os.environ['DOMAINS'].split(',')
            
            if self.scan_domains().empty:
                self.collector.write_blank('domain_scan_results', self._scan_domain({}))

        else:
            self.collector.write_blank('domain_scan_results', self._scan_domain({}))

    def _scan_domain(self,item):
        return {
            "domain" : item.get('domain'),
            "test"   : item.get('test'),
            "result" : bool(item.get('result'))
        }

    def scan_domains(self):
        data = []
        for domain in self.domain_list:
            logging.info(f"Scanning domain: {domain}")
            for i in self.test_domain(domain):
                data.append({
                    "domain" : domain,
                    "test"   : i[0],
                    "result" : i[1]
                })
        df = pd.DataFrame([self._scan_domain(item) for item in data ])
        if df.empty:
            return pd.DataFrame()
        else:
            self.collector.store_df('domain_scan_results', df)
            self.collector.write_df('domain_scan_results')
            return df

    def test_domain(self,domain):
        result = []

        # Check port 80
        try:
            response = requests.get(f"http://{domain}", timeout=5)
            if response.status_code == 200:
                result.append(("port_80", True))
            else:
                result.append(("port_80", False))
        except requests.exceptions.RequestException:
            result.append(("port_80", False))

        # Check port 443
        try:
            response = requests.get(f"https://{domain}", timeout=5)
            if response.status_code == 200:
                result.append(("port_443", True))
            else:
                result.append(("port_443", False))
        except requests.exceptions.RequestException:
            result.append(("port_443", False))

        # Check if port 80 redirects to port 443
        try:
            response = requests.get(f"http://{domain}", allow_redirects=False, timeout=5)
            if response.status_code == 301 and 'Location' in response.headers and response.headers['Location'].startswith('https://'):
                result.append(("redirect_80_to_443", True))
            else:
                result.append(("redirect_80_to_443", False))
        except requests.exceptions.RequestException:
            result.append(("redirect_80_to_443", False))
                
        # Check if port 443 has a valid SSL certificate
        try:   
            response = requests.get(f"https://{domain}", timeout=5)
            if response.status_code == 200:
                result.append(("ssl_certificate_valid", True))
            else:
                result.append(("ssl_certificate_valid", False))
        except requests.exceptions.SSLError:
            result.append(("ssl_certificate_valid", False))
        except requests.exceptions.RequestException:
            result.append(("ssl_certificate_valid", False)) 

        return result

if __name__ == '__main__':
    import sys
    load_dotenv()
    sys.path.append("../")
    sys.path.append("./")
    from collector import Collector
    C = Collector()
    S = Source(C)