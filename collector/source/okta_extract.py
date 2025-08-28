import asyncio
from okta.client import Client as OktaClient
import sys
import logging
import datetime
import os
import random
from dotenv import load_dotenv
import pandas as pd
from urllib.parse import urlparse
import re
import requests
import time
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s'
)

class Source:
    def __init__(self, C):
        self.collector = C

        if C.env({
                'OKTA_DOMAIN': None,
                'OKTA_TOKEN': None,
            }):
        
            self.client = OktaClient({
                'orgUrl': os.environ['OKTA_DOMAIN'],
                'token': os.environ['OKTA_TOKEN']
            })

            # == users    
            logging.info("Starting user extraction...")
            asyncio.run(self.users())

            logging.info("Starting device extraction...")
            asyncio.run(self.devices())

            # # Concurrent factors extraction
            # logging.info("Starting concurrent factors extraction...")
            # asyncio.run(self.factors_concurrent())
            # logging.info(f"Extracted factors for {len(self.flatten)} total factors")
            
            # self.collector.store_df('okta_factors', pd.DataFrame(self.flatten))
            # self.collector.write_df('okta_factors')

            logging.info("Starting logs extraction...")
            self.logs()
        else:
            self.collector.write_blank('okta_users'   , self._okta_users({}))
            self.collector.write_blank('okta_factors' , self._okta_factors({},''))
            self.collector.write_blank('okta_devices' , self._okta_devices({},''))
            self.collector.write_blank('okta_logs'    , self._logs({}))
    
    def is_rate_limit_error(self, exception):
        """Detect if the exception is a rate limit error"""
        error_str = str(exception).lower()
        return any(keyword in error_str for keyword in [
            "rate limit", "429", "too many requests", "quota exceeded"
        ])

    def _okta_factors(self, factor, user_id):
        return {
            "userid"                        : user_id,
            "id"                            : getattr(factor, "id", None),
            "factor_type"                   : getattr(factor, "factor_type", None),
            "provider"                      : getattr(factor, "provider", None),
            "vendor_name"                   : getattr(factor, "vendor_name", None),
            "status"                        : getattr(factor, "status", None),
            "profile_email"                 : getattr(getattr(factor, "profile", None), "email", None),
            "profile_authenticator_name"    : getattr(getattr(factor, "profile", None), "authenticator_name", None),
            "profile_phone_number"          : getattr(getattr(factor, "profile", None), "phone_number", None),
            "profile_credential_id"         : getattr(getattr(factor, "profile", None), "credential_id", None),
            "last_updated"                  : datetime.datetime.strptime(factor.last_updated, "%Y-%m-%dT%H:%M:%S.000Z") if getattr(factor, "last_updated", None) else pd.NaT,
            "verify"                        : getattr(factor, "verify", None),
        }

    async def extract_factors_with_retry(self, user_id, max_retries=3):
        """Extract factors for a user with exponential backoff"""
        for attempt in range(max_retries):
            try:
                logging.debug(f"Extracting factors for user {user_id} (attempt {attempt + 1}/{max_retries})")
                factors, resp, err = await self.client.list_factors(user_id)
                
                if err:
                    logging.error(f"API error for user {user_id}: {err}")
                    if self.is_rate_limit_error(Exception(str(err))):
                        wait_time = (2 ** attempt) + random.random()
                        logging.warning(f"Rate limit in API response for user {user_id}. Retrying in {wait_time:.2f} seconds")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        raise Exception(f"API error: {err}")
                
                user_factors = []
                while True:
                    for factor in factors:
                        user_factors.append(self._okta_factors(factor, user_id))
                    
                    if resp.has_next():
                        factors, err = await resp.next()
                        if err:
                            logging.error(f"Pagination error for user {user_id}: {err}")
                            break
                    else:
                        break
                
                logging.debug(f"Successfully extracted {len(user_factors)} factors for user {user_id}")
                return user_factors
            
            except Exception as e:
                # Check for rate limit specific exceptions
                if self.is_rate_limit_error(e):
                    wait_time = (2 ** attempt) + random.random()
                    logging.warning(f"Rate limit encountered for user {user_id}. Retrying in {wait_time:.2f} seconds")
                    await asyncio.sleep(wait_time)
                else:
                    # For non-rate limit errors, log and re-raise on last attempt
                    logging.error(f"Error extracting factors for user {user_id} (attempt {attempt + 1}): {e}")
                    if attempt == max_retries - 1:
                        raise
                    else:
                        # Wait briefly before retry for non-rate-limit errors
                        await asyncio.sleep(1)
        
        # If all retries fail
        logging.error(f"Failed to extract factors for user {user_id} after {max_retries} attempts")
        return []

    async def factors_concurrent(self):
        """Concurrently extract factors for all users with controlled concurrency"""
        # Limit concurrent requests to avoid overwhelming the API
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent requests
        
        async def limited_extract(user_id):
            async with semaphore:
                return await self.extract_factors_with_retry(user_id)
        
        tasks = [limited_extract(user_id) for user_id in self.users]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results, logging exceptions
        self.flatten = []
        for i, user_factors in enumerate(results):
            if isinstance(user_factors, Exception):
                logging.error(f"Failed to extract factors for user {self.users[i]}: {user_factors}")
            else:
                self.flatten.extend(user_factors)

    def _okta_users(self, user):
        return {
            "id"                            : getattr(user, "id", None),
            "status"                        : getattr(user, "status", None),
            "created"                       : datetime.datetime.strptime(user.created, "%Y-%m-%dT%H:%M:%S.000Z") if getattr(user, "created", None) else pd.NaT,
            "activated"                     : datetime.datetime.strptime(user.activated, "%Y-%m-%dT%H:%M:%S.000Z") if getattr(user, "activated", None) else pd.NaT,
            "status_changed"                : datetime.datetime.strptime(user.status_changed, "%Y-%m-%dT%H:%M:%S.000Z") if getattr(user, "status_changed", None) else pd.NaT,
            "last_login"                    : datetime.datetime.strptime(user.last_login, "%Y-%m-%dT%H:%M:%S.000Z") if getattr(user, "last_login", None) else pd.NaT,
            "last_updated"                  : datetime.datetime.strptime(user.last_updated, "%Y-%m-%dT%H:%M:%S.000Z") if getattr(user, "last_updated", None) else pd.NaT,
            "password_changed"              : datetime.datetime.strptime(user.password_changed, "%Y-%m-%dT%H:%M:%S.000Z") if getattr(user, "password_changed", None) else pd.NaT,
            "type_id"                       : getattr(getattr(user, "type", None), "id", None),
            "profile_login"                 : getattr(getattr(user, "profile", None), "login", None),
            "profile_first_name"            : getattr(getattr(user, "profile", None), "first_name", None),
            "profile_last_name"             : getattr(getattr(user, "profile", None), "last_name", None),
            "profile_nick_name"             : getattr(getattr(user, "profile", None), "nick_name", None),
            "profile_display_name"          : getattr(getattr(user, "profile", None), "display_name", None),
            "profile_email"                 : getattr(getattr(user, "profile", None), "email", None),
            "profile_secondEmail"           : getattr(getattr(user, "profile", None), "secondEmail", None),
            "profile_url"                   : getattr(getattr(user, "profile", None), "profile_url", None),
            "profile_preferred_language"    : getattr(getattr(user, "profile", None), "preferred_language", None),
            "profile_user_type"             : getattr(getattr(user, "profile", None), "user_type", None),
            "profile_organization"          : getattr(getattr(user, "profile", None), "organization", None),
            "profile_title"                 : getattr(getattr(user, "profile", None), "title", None),
            "profile_division"              : getattr(getattr(user, "profile", None), "division", None),
            "profile_department"            : getattr(getattr(user, "profile", None), "department", None),
            "profile_cost_center"           : getattr(getattr(user, "profile", None), "cost_center", None),
            "profile_employee_number"       : getattr(getattr(user, "profile", None), "employee_number", None),
            "profile_mobile_phone"          : getattr(getattr(user, "profile", None), "mobile_phone", None),
            "profile_primary_phone"         : getattr(getattr(user, "profile", None), "primary_phone", None),
            "profile_street_address"        : getattr(getattr(user, "profile", None), "street_address", None),
            "profile_city"                  : getattr(getattr(user, "profile", None), "city", None),
            "profile_state"                 : getattr(getattr(user, "profile", None), "state", None),
            "profile_zip_code"              : getattr(getattr(user, "profile", None), "zip_code", None),
            "profile_country_code"          : getattr(getattr(user, "profile", None), "country_code", None),
        }

    async def users(self):
        flatten_df = []

        self.users = []
        users, resp, err = await self.client.list_users()
        if not err:
            while True:
                for user in users:
                    self.users.append(user.id)  # to be used by factors a bit later
                    flatten_df.append(self._okta_users(user))

                if resp.has_next():
                    users, err = await resp.next()
                else:
                    break
        else:
            logging.error(f"Error fetching users: {err}")
            self.collector.write_blank('okta_users'   , self._okta_users({}))
            return
        
        self.collector.store_df('okta_users', pd.DataFrame(flatten_df))
        self.collector.write_df('okta_users')

    def _okta_devices(self, device):
        return {
            "id": device.get("id"),
            "created": datetime.datetime.strptime(device.get("created"), "%Y-%m-%dT%H:%M:%S.000Z") if device.get("created") else pd.NaT,
            "status": device.get("status"),
            "lastupdated": datetime.datetime.strptime(device.get("lastUpdated"), "%Y-%m-%dT%H:%M:%S.000Z") if device.get("lastUpdated") else pd.NaT,
            "profile_displayname": device.get("profile", {}).get("displayName"),
            "profile_platform": device.get("profile", {}).get("platform"),
            "profile_manufacturer": device.get("profile", {}).get("manufacturer"),
            "profile_model": device.get("profile", {}).get("model"),
            "profile_osversion": device.get("profile", {}).get("osVersion"),
            "profile_registered": bool(device.get("profile", {}).get("registered")) if device.get("profile", {}).get("registered") is not None else None,
            "profile_securehardwarepresent": bool(device.get("profile", {}).get("secureHardwarePresent")) if device.get("profile", {}).get("secureHardwarePresent") is not None else None,
            "profile_authenticatorappkey": device.get("profile", {}).get("authenticatorAppKey"),
            "resourcetype": device.get("resourceType"),
            "resourcedisplayname_value": device.get("resourceDisplayName", {}).get("value"),
            "resourcedisplayname_sensitive": bool(device.get("resourceDisplayName", {}).get("sensitive")) if device.get("resourceDisplayName", {}).get("sensitive") is not None else None,
            "resourceid": device.get("resourceId"),
            "resourcealternateid": device.get("resourceAlternateId"),
        }
    
    async def devices(self):
        flatten_df = []
        next_url = '/api/v1/devices'
        
        try:
            while next_url:
                # Use generic request executor since list_devices() doesn't exist
                request, error = await self.client.get_request_executor().create_request(
                    method='GET',
                    url=next_url,
                    body={},
                    headers={}
                )
                
                if error:
                    logging.error(f"Error creating devices request: {error}")
                    self.collector.write_blank('okta_devices', self._okta_devices({}))
                    return
                    
                response, error = await self.client.get_request_executor().execute(request, None)
                
                if error:
                    logging.error(f"Error executing devices request: {error}")
                    self.collector.write_blank('okta_devices', self._okta_devices({}))
                    return
                    
                # Get the response body
                devices_data = response.get_body()
                
                if devices_data:
                    for device in devices_data:
                        flatten_df.append(self._okta_devices(device))
                    
                    # Handle pagination by checking Link header
                    next_url = None
                    headers = response.get_headers()
                    
                    if headers and 'Link' in headers:             
                        link_header = ';'.join(headers.getall('Link'))
                        # Parse Link header to find next page URL
                        # Format: <url>; rel="next", <url>; rel="prev"
                        next_match = re.search(r'<([^>]+)>;\s*rel="next"', link_header)
                        if next_match:
                            next_url = next_match.group(1)
                            # Extract just the path if it's a full URL
                            if next_url.startswith('http'):
                                parsed = urlparse(next_url)
                                next_url = parsed.path + ('?' + parsed.query if parsed.query else '')
                            logging.debug(f"Found next page URL: {next_url}")
                    
                    logging.debug(f"Processed {len(devices_data)} devices, next_url: {next_url}")
                else:
                    logging.warning("No devices found in response")
                    break
                
        except Exception as e:
            logging.error(f"Unexpected error fetching devices: {e}")
            self.collector.write_blank('okta_devices', self._okta_devices({}))
            return
        
        if flatten_df:
            self.collector.store_df('okta_devices', pd.DataFrame(flatten_df))
            logging.info(f"Successfully processed {len(flatten_df)} total devices")
        else:
            self.collector.write_blank('okta_devices', self._okta_devices({}))
            
        self.collector.write_df('okta_devices')

    def _logs(self, log):
        if not log or not isinstance(log, dict):
            log = {}
        
        return {
            "uuid": log.get("uuid"),
            "published": datetime.datetime.strptime(log.get("published"), "%Y-%m-%dT%H:%M:%S.%fZ") if log.get("published") else pd.NaT,
            "eventtype": log.get("eventType"),
            "version": log.get("version"),
            "severity": log.get("severity"),
            "legacyeventtype": log.get("legacyEventType"),
            "displaymessage": log.get("displayMessage"),
            "actor_id": log.get("actor", {}).get("id") if log.get("actor") else None,
            "actor_type": log.get("actor", {}).get("type") if log.get("actor") else None,
            "actor_alternateid": log.get("actor", {}).get("alternateId") if log.get("actor") else None,
            "actor_displayname": log.get("actor", {}).get("displayName") if log.get("actor") else None,
            "client_useragent_rawuseragent": log.get("client", {}).get("userAgent", {}).get("rawUserAgent") if log.get("client") and log.get("client", {}).get("userAgent") else None,
            "client_useragent_os": log.get("client", {}).get("userAgent", {}).get("os") if log.get("client") and log.get("client", {}).get("userAgent") else None,
            "client_useragent_browser": log.get("client", {}).get("userAgent", {}).get("browser") if log.get("client") and log.get("client", {}).get("userAgent") else None,
            "client_zone": log.get("client", {}).get("zone") if log.get("client") else None,
            "client_device": log.get("client", {}).get("device") if log.get("client") else None,
            "client_id": log.get("client", {}).get("id") if log.get("client") else None,
            "client_ipaddress": log.get("client", {}).get("ipAddress") if log.get("client") else None,
            "client_geographicalcontext_city": log.get("client", {}).get("geographicalContext", {}).get("city") if log.get("client") and log.get("client", {}).get("geographicalContext") else None,
            "client_geographicalcontext_state": log.get("client", {}).get("geographicalContext", {}).get("state") if log.get("client") and log.get("client", {}).get("geographicalContext") else None,
            "client_geographicalcontext_country": log.get("client", {}).get("geographicalContext", {}).get("country") if log.get("client") and log.get("client", {}).get("geographicalContext") else None,
            "client_geographicalcontext_postalcode": log.get("client", {}).get("geographicalContext", {}).get("postalCode") if log.get("client") and log.get("client", {}).get("geographicalContext") else None,
            "client_geographicalcontext_geolocation_lat": log.get("client", {}).get("geographicalContext", {}).get("geolocation", {}).get("lat") if log.get("client") and log.get("client", {}).get("geographicalContext") and log.get("client", {}).get("geographicalContext", {}).get("geolocation") else None,
            "client_geographicalcontext_geolocation_lon": log.get("client", {}).get("geographicalContext", {}).get("geolocation", {}).get("lon") if log.get("client") and log.get("client", {}).get("geographicalContext") and log.get("client", {}).get("geographicalContext", {}).get("geolocation") else None,
            "outcome_result": log.get("outcome", {}).get("result") if log.get("outcome") else None,
            "outcome_reason": log.get("outcome", {}).get("reason") if log.get("outcome") else None,
            "target_id": log.get("target", [{}])[0].get("id") if log.get("target") and len(log.get("target")) > 0 and log.get("target")[0] else None,
            "target_type": log.get("target", [{}])[0].get("type") if log.get("target") and len(log.get("target")) > 0 and log.get("target")[0] else None,
            "target_alternateid": log.get("target", [{}])[0].get("alternateId") if log.get("target") and len(log.get("target")) > 0 and log.get("target")[0] else None,
            "target_displayname": log.get("target", [{}])[0].get("displayName") if log.get("target") and len(log.get("target")) > 0 and log.get("target")[0] else None,
            "transaction_type": log.get("transaction", {}).get("type") if log.get("transaction") else None,
            "transaction_id": log.get("transaction", {}).get("id") if log.get("transaction") else None,
            "transaction_detail": json.dumps(log.get("transaction", {}).get("detail")) if log.get("transaction") and log.get("transaction", {}).get("detail") else None,
            "debugcontext_debugdata": json.dumps(log.get("debugContext", {}).get("debugData")) if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "authenticationcontext_authenticationprovider": log.get("authenticationContext", {}).get("authenticationProvider") if log.get("authenticationContext") else None,
            "authenticationcontext_authenticationstep": log.get("authenticationContext", {}).get("authenticationStep") if log.get("authenticationContext") else None,
            "authenticationcontext_credentialprovider": log.get("authenticationContext", {}).get("credentialProvider") if log.get("authenticationContext") else None,
            "authenticationcontext_credentialtype": log.get("authenticationContext", {}).get("credentialType") if log.get("authenticationContext") else None,
            "authenticationcontext_issuer": log.get("authenticationContext", {}).get("issuer") if log.get("authenticationContext") else None,
            "authenticationcontext_externalSessionId": log.get("authenticationContext", {}).get("externalSessionId") if log.get("authenticationContext") else None,
            "securitycontext_aswellknown": log.get("securityContext", {}).get("asWellKnown") if log.get("securityContext") else None,
            "securitycontext_asos": log.get("securityContext", {}).get("asOrg") if log.get("securityContext") else None,
            "securitycontext_asisp": log.get("securityContext", {}).get("asIsp") if log.get("securityContext") else None,
            "securitycontext_domain": log.get("securityContext", {}).get("domain") if log.get("securityContext") else None,
            "securitycontext_isthreat": log.get("securityContext", {}).get("isThreat") if log.get("securityContext") else None,
            "securitycontext_istunnelinganonymizer": log.get("securityContext", {}).get("isTunnelingAnonymizer") if log.get("securityContext") else None,
            "securitycontext_istorexitnode": log.get("securityContext", {}).get("isTorExitNode") if log.get("securityContext") else None,
        }

    def logs(self):
        try:
            domain = os.environ['OKTA_DOMAIN'].rstrip('/')
            token = os.environ['OKTA_TOKEN']
            
            since = (datetime.datetime.now() - datetime.timedelta(hours=26)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
            
            url = f"{domain}/api/v1/logs"
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': f'SSWS {token}'
            }
            params = {
                'since': since,
                'limit': 1000
            }
            
            flatten_df = []
            
            while url:
                logging.debug(f"Fetching logs from: {url}")
                
                response = requests.get(url, headers=headers, params=params if url == f"{domain}/api/v1/logs" else None)
                
                if response.status_code == 429:
                    rate_limit_reset = response.headers.get('X-Rate-Limit-Reset')
                    if rate_limit_reset:
                        wait_time = int(rate_limit_reset) - int(time.time()) + 1
                        logging.warning(f"Rate limit hit. Waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        time.sleep(60)
                        continue
                
                if response.status_code != 200:
                    logging.error(f"Error fetching logs: {response.status_code} - {response.text}")
                    break
                
                try:
                    logs_data = response.json()
                except ValueError as e:
                    logging.error(f"Failed to parse JSON response: {e}")
                    break
                
                if not logs_data or not isinstance(logs_data, list):
                    logging.info("No more logs found or invalid data format")
                    break
                
                for log in logs_data:
                    if log and isinstance(log, dict):
                        flatten_df.append(self._logs(log))
                    else:
                        logging.warning(f"Skipping invalid log entry: {log}")
                
                logging.info(f"Processed {len(logs_data)} logs")
                
                next_url = None
                if 'Link' in response.headers:
                    link_header = response.headers['Link']
                    next_match = re.search(r'<([^>]+)>;\s*rel="next"', link_header)
                    if next_match:
                        next_url = next_match.group(1)
                        logging.debug(f"Found next page URL: {next_url}")
                
                url = next_url
                params = None
            
            if flatten_df:
                self.collector.store_df('okta_logs', pd.DataFrame(flatten_df))
                logging.info(f"Successfully processed {len(flatten_df)} total logs")
            else:
                self.collector.write_blank('okta_logs', self._logs({}))
                
            self.collector.write_df('okta_logs')
            
        except Exception as e:
            logging.error(f"Error extracting logs: {e}")
            self.collector.write_blank('okta_logs', self._logs({}))
            self.collector.write_df('okta_logs')

# == we create the __main__ bit to allow the plugin to be manually run when needed.
if __name__ == '__main__':
    import sys
    load_dotenv()
    sys.path.append("../")
    sys.path.append("./")
    from collector import Collector
    C = Collector()
    S = Source(C)
