import asyncio
from okta.client import Client as OktaClient
import sys
import logging
import datetime
import os
import random
from dotenv import load_dotenv
import pandas as pd

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
            logging.info(f"Extracted {len(self.users)} users")

            # Concurrent factors extraction
            logging.info("Starting concurrent factors extraction...")
            asyncio.run(self.factors_concurrent())
            logging.info(f"Extracted factors for {len(self.flatten)} total factors")
            
            self.collector.store_df('okta_factors', pd.DataFrame(self.flatten))
            self.collector.write_df('okta_factors')
        else:
            self.collector.write_blank('okta_users'   , self._okta_users({}))
            self.collector.write_blank('okta_factors' , self._okta_factors({},''))
    
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

# == we create the __main__ bit to allow the plugin to be manually run when needed.
if __name__ == '__main__':
    import sys
    load_dotenv()
    sys.path.append("../")
    sys.path.append("./")
    from collector import Collector
    C = Collector()
    S = Source(C)
