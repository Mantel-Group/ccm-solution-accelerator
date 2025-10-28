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
        self.device_ids = []
        self.device_users_flatten = []

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

            # Device users extraction
            if self.device_ids:
                logging.info("Starting device users extraction...")
                asyncio.run(self.device_users_concurrent())
                if self.device_users_flatten:
                    self.collector.store_df('okta_device_users', pd.DataFrame(self.device_users_flatten))
                    self.collector.write_df('okta_device_users')
                else:
                    self.collector.write_blank('okta_device_users', self._okta_device_users({}, ''))
            else:
                self.collector.write_blank('okta_device_users', self._okta_device_users({}, ''))

            logging.info("Starting logs extraction...")
            self.logs()
        else:
            self.collector.write_blank('okta_users'       , self._okta_users({}))
            self.collector.write_blank('okta_factors'     , self._okta_factors({},''))
            self.collector.write_blank('okta_devices'     , self._okta_devices({}))
            self.collector.write_blank('okta_device_users', self._okta_device_users({}, ''))
            self.collector.write_blank('okta_logs'        , self._logs({}))
    
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

    def _okta_device_users(self, device_user_data, device_id):
        return {
            "device_id": device_id,
            "created": datetime.datetime.strptime(device_user_data.get("created"), "%Y-%m-%dT%H:%M:%S.000Z") if device_user_data.get("created") else pd.NaT,
            "managementstatus": device_user_data.get("managementStatus"),
            "user_id": device_user_data.get("user", {}).get("id") if device_user_data.get("user") else None,
            "user_status": device_user_data.get("user", {}).get("status") if device_user_data.get("user") else None,
            "user_displayname": device_user_data.get("user", {}).get("displayName") if device_user_data.get("user") else None,
            "user_created": datetime.datetime.strptime(device_user_data.get("user", {}).get("created"), "%Y-%m-%dT%H:%M:%S.000Z") if device_user_data.get("user", {}).get("created") else pd.NaT,
        }

    async def extract_device_users_with_retry(self, device_id, max_retries=3):
        """Extract device users for a device with exponential backoff"""
        for attempt in range(max_retries):
            try:
                logging.debug(f"Extracting device users for device {device_id} (attempt {attempt + 1}/{max_retries})")

                request, error = await self.client.get_request_executor().create_request(
                    method='GET',
                    url=f'/api/v1/devices/{device_id}/users',
                    body={},
                    headers={}
                )

                if error:
                    logging.error(f"Error creating device users request for device {device_id}: {error}")
                    if self.is_rate_limit_error(Exception(str(error))):
                        wait_time = (2 ** attempt) + random.random()
                        logging.warning(f"Rate limit in API response for device {device_id}. Retrying in {wait_time:.2f} seconds")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        raise Exception(f"API error: {error}")

                response, error = await self.client.get_request_executor().execute(request, None)

                if error:
                    logging.error(f"Error executing device users request for device {device_id}: {error}")
                    if self.is_rate_limit_error(Exception(str(error))):
                        wait_time = (2 ** attempt) + random.random()
                        logging.warning(f"Rate limit in API response for device {device_id}. Retrying in {wait_time:.2f} seconds")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        raise Exception(f"API error: {error}")

                device_users_data = response.get_body()
                device_user_records = []

                if device_users_data:
                    next_url = None

                    while True:
                        for device_user in device_users_data:
                            device_user_records.append(self._okta_device_users(device_user, device_id))

                        # Handle pagination by checking Link header
                        headers = response.get_headers()
                        if headers and 'Link' in headers:
                            link_header = ';'.join(headers.getall('Link'))
                            next_match = re.search(r'<([^>]+)>;\s*rel="next"', link_header)
                            if next_match:
                                next_url = next_match.group(1)
                                if next_url.startswith('http'):
                                    parsed = urlparse(next_url)
                                    next_url = parsed.path + ('?' + parsed.query if parsed.query else '')

                                # Fetch next page
                                request, error = await self.client.get_request_executor().create_request(
                                    method='GET',
                                    url=next_url,
                                    body={},
                                    headers={}
                                )

                                if error:
                                    logging.error(f"Pagination error for device {device_id}: {error}")
                                    break

                                response, error = await self.client.get_request_executor().execute(request, None)

                                if error:
                                    logging.error(f"Pagination error for device {device_id}: {error}")
                                    break

                                device_users_data = response.get_body()
                            else:
                                break
                        else:
                            break

                logging.debug(f"Successfully extracted {len(device_user_records)} device users for device {device_id}")
                return device_user_records

            except Exception as e:
                # Check for rate limit specific exceptions
                if self.is_rate_limit_error(e):
                    wait_time = (2 ** attempt) + random.random()
                    logging.warning(f"Rate limit encountered for device {device_id}. Retrying in {wait_time:.2f} seconds")
                    await asyncio.sleep(wait_time)
                else:
                    # For non-rate limit errors, log and re-raise on last attempt
                    logging.error(f"Error extracting device users for device {device_id} (attempt {attempt + 1}): {e}")
                    if attempt == max_retries - 1:
                        logging.error(f"Failed to extract device users for device {device_id} after {max_retries} attempts")
                        return []
                    else:
                        # Wait briefly before retry for non-rate-limit errors
                        await asyncio.sleep(1)

        # If all retries fail
        logging.error(f"Failed to extract device users for device {device_id} after {max_retries} attempts")
        return []

    async def device_users_concurrent(self):
        """Concurrently extract device users for all devices with controlled concurrency"""
        # Limit concurrent requests to avoid overwhelming the API
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent requests

        async def limited_extract(device_id):
            async with semaphore:
                return await self.extract_device_users_with_retry(device_id)

        tasks = [limited_extract(device_id) for device_id in self.device_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Flatten results, logging exceptions
        self.device_users_flatten = []
        for i, device_user_records in enumerate(results):
            if isinstance(device_user_records, Exception):
                logging.error(f"Failed to extract device users for device {self.device_ids[i]}: {device_user_records}")
            else:
                self.device_users_flatten.extend(device_user_records)

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

        # Store device IDs for later use by device_users extraction
        self.device_ids = [d['id'] for d in flatten_df if d.get('id')]

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
            "debugcontext_debugdata_accessrequestapprovalsequenceid": log.get("debugContext", {}).get("debugData", {}).get("accessRequestApprovalSequenceId") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_accessrequestid": log.get("debugContext", {}).get("debugData", {}).get("accessRequestId") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_accessrequestmatchedconditionid": log.get("debugContext", {}).get("debugData", {}).get("accessRequestMatchedConditionId") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_accessrequestsubject": log.get("debugContext", {}).get("debugData", {}).get("accessRequestSubject") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_accessscopeid": log.get("debugContext", {}).get("debugData", {}).get("accessScopeId") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_accessscopetype": log.get("debugContext", {}).get("debugData", {}).get("accessScopeType") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_anonymizerstatus": log.get("debugContext", {}).get("debugData", {}).get("anonymizerStatus") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_appcontextname": log.get("debugContext", {}).get("debugData", {}).get("appContextName") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_appeventispersonal": log.get("debugContext", {}).get("debugData", {}).get("appEventIsPersonal") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_appname": log.get("debugContext", {}).get("debugData", {}).get("appName") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_appuserid": log.get("debugContext", {}).get("debugData", {}).get("appUserId") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_appusername": log.get("debugContext", {}).get("debugData", {}).get("appUsername") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_appname2": log.get("debugContext", {}).get("debugData", {}).get("appname") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_audience": log.get("debugContext", {}).get("debugData", {}).get("audience") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_authcode": log.get("debugContext", {}).get("debugData", {}).get("authCode") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_authmethodfifthenrollment": log.get("debugContext", {}).get("debugData", {}).get("authMethodFifthEnrollment") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_authmethodfifthtype": log.get("debugContext", {}).get("debugData", {}).get("authMethodFifthType") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_authmethodfifthverificationtime": log.get("debugContext", {}).get("debugData", {}).get("authMethodFifthVerificationTime") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_authmethodfirstenrollment": log.get("debugContext", {}).get("debugData", {}).get("authMethodFirstEnrollment") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_authmethodfirsttype": log.get("debugContext", {}).get("debugData", {}).get("authMethodFirstType") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_authmethodfirstverificationtime": log.get("debugContext", {}).get("debugData", {}).get("authMethodFirstVerificationTime") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_authmethodfourthenrollment": log.get("debugContext", {}).get("debugData", {}).get("authMethodFourthEnrollment") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_authmethodfourthtype": log.get("debugContext", {}).get("debugData", {}).get("authMethodFourthType") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_authmethodfourthverificationtime": log.get("debugContext", {}).get("debugData", {}).get("authMethodFourthVerificationTime") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_authmethodsecondenrollment": log.get("debugContext", {}).get("debugData", {}).get("authMethodSecondEnrollment") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_authmethodsecondtype": log.get("debugContext", {}).get("debugData", {}).get("authMethodSecondType") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_authmethodsecondverificationtime": log.get("debugContext", {}).get("debugData", {}).get("authMethodSecondVerificationTime") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_authmethodthirdenrollment": log.get("debugContext", {}).get("debugData", {}).get("authMethodThirdEnrollment") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_authmethodthirdtype": log.get("debugContext", {}).get("debugData", {}).get("authMethodThirdType") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_authmethodthirdverificationtime": log.get("debugContext", {}).get("debugData", {}).get("authMethodThirdVerificationTime") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_authtime": log.get("debugContext", {}).get("debugData", {}).get("authTime") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_authenticationclassref": log.get("debugContext", {}).get("debugData", {}).get("authenticationClassRef") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_authenticatormethodchallengetime": log.get("debugContext", {}).get("debugData", {}).get("authenticatorMethodChallengeTime") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_authnrequestid": log.get("debugContext", {}).get("debugData", {}).get("authnRequestId") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_behaviors": log.get("debugContext", {}).get("debugData", {}).get("behaviors") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_canceledat": log.get("debugContext", {}).get("debugData", {}).get("canceledAt") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_category": log.get("debugContext", {}).get("debugData", {}).get("category") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_causes": log.get("debugContext", {}).get("debugData", {}).get("causes") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_challengeauthenticatorslist": log.get("debugContext", {}).get("debugData", {}).get("challengeAuthenticatorsList") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_changedattributes": log.get("debugContext", {}).get("debugData", {}).get("changedAttributes") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_changeddevicesignals": log.get("debugContext", {}).get("debugData", {}).get("changedDeviceSignals") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_clientauthtype": log.get("debugContext", {}).get("debugData", {}).get("clientAuthType") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_clientsecret": log.get("debugContext", {}).get("debugData", {}).get("clientSecret") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_devicecategory": log.get("debugContext", {}).get("debugData", {}).get("deviceCategory") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_devicefingerprint": log.get("debugContext", {}).get("debugData", {}).get("deviceFingerprint") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_deviceplatform": log.get("debugContext", {}).get("debugData", {}).get("devicePlatform") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_dthash": log.get("debugContext", {}).get("debugData", {}).get("dtHash") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_emailprovider": log.get("debugContext", {}).get("debugData", {}).get("emailProvider") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_emailrequestid": log.get("debugContext", {}).get("debugData", {}).get("emailRequestId") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_endedsessionid": log.get("debugContext", {}).get("debugData", {}).get("endedSessionId") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_errormessage": log.get("debugContext", {}).get("debugData", {}).get("errorMessage") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_expirytime": log.get("debugContext", {}).get("debugData", {}).get("expiryTime") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_externalsessionid": log.get("debugContext", {}).get("debugData", {}).get("externalSessionId") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_factor": log.get("debugContext", {}).get("debugData", {}).get("factor") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_factorintent": log.get("debugContext", {}).get("debugData", {}).get("factorIntent") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_fedbrokermode": log.get("debugContext", {}).get("debugData", {}).get("fedBrokerMode") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_grantaction": log.get("debugContext", {}).get("debugData", {}).get("grantAction") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_grantid": log.get("debugContext", {}).get("debugData", {}).get("grantId") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_grantsource": log.get("debugContext", {}).get("debugData", {}).get("grantSource") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_granttype": log.get("debugContext", {}).get("debugData", {}).get("grantType") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_grantedscopes": log.get("debugContext", {}).get("debugData", {}).get("grantedScopes") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_idptype": log.get("debugContext", {}).get("debugData", {}).get("idpType") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_initiationtype": log.get("debugContext", {}).get("debugData", {}).get("initiationType") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_issuedat": log.get("debugContext", {}).get("debugData", {}).get("issuedAt") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_issuer": log.get("debugContext", {}).get("debugData", {}).get("issuer") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_jti": log.get("debugContext", {}).get("debugData", {}).get("jti") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_keytypeusedforauthentication": log.get("debugContext", {}).get("debugData", {}).get("keyTypeUsedForAuthentication") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_lastresolvedat": log.get("debugContext", {}).get("debugData", {}).get("lastResolvedAt") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_logonlysecuritydata": log.get("debugContext", {}).get("debugData", {}).get("logOnlySecurityData") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_loginresult": log.get("debugContext", {}).get("debugData", {}).get("loginResult") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_message": log.get("debugContext", {}).get("debugData", {}).get("message") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_newipaddress": log.get("debugContext", {}).get("debugData", {}).get("newIpAddress") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_o365immutableid": log.get("debugContext", {}).get("debugData", {}).get("o365Immutableid") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_oktauseragentextended": log.get("debugContext", {}).get("debugData", {}).get("oktaUserAgentExtended") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_oktausername": log.get("debugContext", {}).get("debugData", {}).get("oktaUsername") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_operationratelimitscopetype": log.get("debugContext", {}).get("debugData", {}).get("operationRateLimitScopeType") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_operationratelimitsecondsreset": log.get("debugContext", {}).get("debugData", {}).get("operationRateLimitSecondsToReset") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_operationratelimitsubtype": log.get("debugContext", {}).get("debugData", {}).get("operationRateLimitSubtype") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_operationratelimitthreshold": log.get("debugContext", {}).get("debugData", {}).get("operationRateLimitThreshold") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_operationratelimittimespan": log.get("debugContext", {}).get("debugData", {}).get("operationRateLimitTimeSpan") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_operationratelimittimeunit": log.get("debugContext", {}).get("debugData", {}).get("operationRateLimitTimeUnit") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_operationratelimittype": log.get("debugContext", {}).get("debugData", {}).get("operationRateLimitType") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_origin": log.get("debugContext", {}).get("debugData", {}).get("origin") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_permalinkid": log.get("debugContext", {}).get("debugData", {}).get("permalinkId") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_pluginversion": log.get("debugContext", {}).get("debugData", {}).get("pluginVersion") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_previousipaddress": log.get("debugContext", {}).get("debugData", {}).get("previousIpAddress") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_principalentitlementschangesurl": log.get("debugContext", {}).get("debugData", {}).get("principalEntitlementsChangesUrl") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_privilegegranted": log.get("debugContext", {}).get("debugData", {}).get("privilegeGranted") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_proxytype": log.get("debugContext", {}).get("debugData", {}).get("proxyType") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_pushonlyresponsetype": log.get("debugContext", {}).get("debugData", {}).get("pushOnlyResponseType") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_pushwithnumberchallengeresponsetype": log.get("debugContext", {}).get("debugData", {}).get("pushWithNumberChallengeResponseType") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_redirecturi": log.get("debugContext", {}).get("debugData", {}).get("redirectUri") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_requestid": log.get("debugContext", {}).get("debugData", {}).get("requestId") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_requesturi": log.get("debugContext", {}).get("debugData", {}).get("requestUri") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_requestedforid": log.get("debugContext", {}).get("debugData", {}).get("requestedForId") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_requestedresourceid": log.get("debugContext", {}).get("debugData", {}).get("requestedResourceId") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_requestedresourcetype": log.get("debugContext", {}).get("debugData", {}).get("requestedResourceType") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_requestedscopes": log.get("debugContext", {}).get("debugData", {}).get("requestedScopes") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_requesterid": log.get("debugContext", {}).get("debugData", {}).get("requesterId") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_responsemode": log.get("debugContext", {}).get("debugData", {}).get("responseMode") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_responsetime": log.get("debugContext", {}).get("debugData", {}).get("responseTime") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_responsetype": log.get("debugContext", {}).get("debugData", {}).get("responseType") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_risk": log.get("debugContext", {}).get("debugData", {}).get("risk") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_risksettingsrequestsubmissiontype": log.get("debugContext", {}).get("debugData", {}).get("riskSettingsRequestSubmissionType") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_ruleconflictdetails": log.get("debugContext", {}).get("debugData", {}).get("ruleConflictDetails") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_scriptname": log.get("debugContext", {}).get("debugData", {}).get("scriptName") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_signonmode": log.get("debugContext", {}).get("debugData", {}).get("signOnMode") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_source": log.get("debugContext", {}).get("debugData", {}).get("source") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_state": log.get("debugContext", {}).get("debugData", {}).get("state") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_subject": log.get("debugContext", {}).get("debugData", {}).get("subject") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_successfuldeactivations": log.get("debugContext", {}).get("debugData", {}).get("successfulDeactivations") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_successfuldeletions": log.get("debugContext", {}).get("debugData", {}).get("successfulDeletions") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_successfulsuspensions": log.get("debugContext", {}).get("debugData", {}).get("successfulSuspensions") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_targeteventhookids": log.get("debugContext", {}).get("debugData", {}).get("targetEventHookIds") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_threatsuspected": log.get("debugContext", {}).get("debugData", {}).get("threatSuspected") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_traceid": log.get("debugContext", {}).get("debugData", {}).get("traceId") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_tunnels": log.get("debugContext", {}).get("debugData", {}).get("tunnels") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_url": log.get("debugContext", {}).get("debugData", {}).get("url") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_userid": log.get("debugContext", {}).get("debugData", {}).get("userId") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
            "debugcontext_debugdata_usercomment": log.get("debugContext", {}).get("debugData", {}).get("usercomment") if log.get("debugContext") and log.get("debugContext", {}).get("debugData") else None,
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
