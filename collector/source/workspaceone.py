import requests
import os
import logging
import time
import pandas as pd
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s'
)


class Source:
    def __init__(self, C):
        self.collector = C

        if C.env({
            'WORKSPACEONE_CLIENTID':    None,
            'WORKSPACEONE_CLIENTSECRET': None,
            'WORKSPACEONE_API_SERVER':  None,
            'WORKSPACEONE_TOKEN_URL':   'https://apac.uemauth.workspaceone.com/connect/token',
        }):
            self._authenticate()

            if self.computers().empty:
                self.collector.write_blank('workspaceone_computers', self._computer({}))
        else:
            self.collector.write_blank('workspaceone_computers', self._computer({}))

    def _authenticate(self) -> None:
        token_url = os.environ['WORKSPACEONE_TOKEN_URL']
        max_connect_retries = 2

        for attempt in range(max_connect_retries + 1):
            try:
                req = requests.post(
                    token_url,
                    data={
                        'grant_type':    'client_credentials',
                        'client_id':     os.environ['WORKSPACEONE_CLIENTID'],
                        'client_secret': os.environ['WORKSPACEONE_CLIENTSECRET'],
                    },
                    timeout=30,
                )
                req.raise_for_status()
                access_token = req.json()['access_token']
                self.headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Accept':        'application/json;version=3',
                    'Content-Type':  'application/json',
                }
                logging.info('WorkspaceOne authentication succeeded')
                return
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as err:
                if attempt < max_connect_retries:
                    logging.warning(f'Auth connection error (attempt {attempt + 1}/{max_connect_retries + 1}). Retrying in 5s: {err}')
                    time.sleep(5)
                else:
                    logging.error(f'WorkspaceOne authentication failed after {max_connect_retries + 1} attempts: {err}')
                    raise
            except requests.exceptions.HTTPError as err:
                logging.error(f'WorkspaceOne authentication failed: {err}')
                raise

    def _make_request(self, url: str, params: dict = None, max_retries: int = 5, max_connect_retries: int = 2) -> requests.Response:
        retry_delay = 15

        for attempt in range(max_retries):
            try:
                req = requests.get(url, headers=self.headers, params=params, timeout=60)
                req.raise_for_status()
                return req
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as err:
                if attempt < max_connect_retries:
                    logging.warning(f'Connection error (attempt {attempt + 1}/{max_connect_retries + 1}). Retrying in 5s: {err}')
                    time.sleep(5)
                else:
                    logging.error(f'Connection failed after {max_connect_retries + 1} attempts for URL: {url}: {err}')
                    raise
            except requests.exceptions.HTTPError as err:
                if err.response.status_code == 429:
                    if attempt < max_retries - 1:
                        logging.warning(f'Rate limit hit (429). Retrying in {retry_delay}s (attempt {attempt + 1}/{max_retries}).')
                        time.sleep(retry_delay)
                        retry_delay = min(retry_delay * 2, 300)
                    else:
                        logging.error(f'Rate limit exceeded after {max_retries} attempts for URL: {url}')
                        raise
                else:
                    raise

        return None

    def _computer(self, item: dict) -> dict:
        id_field = item.get('Id', {})
        raw_id = id_field.get('Value') if isinstance(id_field, dict) else id_field
        device_id = str(raw_id) if raw_id is not None else None

        # Extract IP from the first populated device_network_info entry
        ip_address = None
        for net in item.get('device_network_info', []):
            ip_address = net.get('ip_address') or net.get('IpAddress')
            if ip_address:
                break

        return {
            'device_id':              device_id,
            'uuid':                   item.get('Uuid'),
            'udid':                   item.get('udid'),
            'serial_number':          item.get('serial_number'),
            'mac_address':            item.get('mac_address'),
            'imei':                   item.get('imei'),
            'asset_number':           item.get('asset_number'),
            'device_friendly_name':   item.get('device_friendly_name'),
            'device_reported_name':   item.get('device_reported_name'),
            'ip_address':             ip_address,
            'platform_name':          item.get('platform_name'),
            'device_type':            item.get('device_type'),
            'model_identifier':       item.get('model_identifier'),
            'model':                  item.get('model'),
            'operating_system':       item.get('operating_system'),
            'os_build_version':       item.get('os_build_version'),
            'last_seen':              item.get('last_seen'),
            'last_enrolled_on':       item.get('last_enrolled_on'),
            'enrollment_status':      item.get('enrollment_status'),
            'compliance_status':      item.get('compliance_status'),
            'compromised_status':     item.get('compromised_status'),
            'is_supervised':          item.get('is_supervised'),
            'ownership':              item.get('ownership'),
            'organization_group_name': item.get('organization_group_name'),
            'organization_group_uuid': item.get('organization_group_uuid'),
            'enrollment_user_name':   item.get('enrollment_user_name'),
            'enrollment_user_uuid':   item.get('enrollment_user_uuid'),
            'enrollment_user_email':  item.get('enrollment_user_email_address'),
            'managed_by':             item.get('managed_by'),
            'time_zone':              item.get('time_zone'),
        }

    def computers(self) -> pd.DataFrame:
        logging.info('Starting extraction: workspaceone_computers')
        base_url = f"https://{os.environ['WORKSPACEONE_API_SERVER']}/API/mdm/devices/search"
        page_size = 500
        page = 0
        fetched = 0

        while True:
            try:
                req = self._make_request(base_url, params={'pagesize': page_size, 'page': page})
                if req is None:
                    break
            except requests.exceptions.HTTPError as err:
                logging.error(f'API error fetching workspaceone_computers page {page}: {err}')
                raise

            body = req.json()
            results = body.get('devices', [])
            if not results:
                break

            total = body.get('total', 0)
            fetched += len(results)
            logging.info(f'Page {page}: retrieved {fetched} of {total} devices')

            df = pd.DataFrame([self._computer(item) for item in results])
            self.collector.store_df('workspaceone_computers', df)

            if fetched >= total:
                break
            page += 1

        self.collector.write_df('workspaceone_computers')
        return self.collector.df.get('workspaceone_computers', pd.DataFrame())


# == we create the __main__ bit to allow the plugin to be manually run when needed.
if __name__ == '__main__':
    import sys
    load_dotenv()
    sys.path.append('../')
    sys.path.append('./')
    from collector import Collector
    C = Collector()
    S = Source(C)
