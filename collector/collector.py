import os
import pandas as pd
import importlib
import datetime
import requests
from dotenv import load_dotenv
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging
from urllib.parse import quote
import uuid
import traceback
import duckdb
from alert import Alert
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed

# Suppress DuckDB engine warning about index reflection
warnings.filterwarnings("ignore", message="duckdb-engine doesn't yet support reflection on indices")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
)

class Collector:
    def __init__(self):
        load_dotenv('../.env')
        self.name = None
        self.sync_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.collection_start = datetime.datetime.now()
        self.alert = Alert()
        self.df = {}
        self.schema_created = {}
        self.row_count = {}
        self.write_errors: list[str] = []
        
        # Initialize database uploaders
        self.postgres_uploader = UploadPostgress(self)
        self.duckdb_uploader = UploadDuckDB(self)
        self.bigquery_uploader = UploadBigQuery(self)
        
    '''Check if the environment variables are available'''
    def env(self,X):
        ok = True
        data = {}
        for x in X:
            if X[x] is not None:
                data[x] = X[x]
                os.environ[x] = X[x]
            if x not in os.environ:
                if data.get(x) is None:
                    logging.debug(f"Environment variable {x} not found - plugin be skipped")
                    ok = False
            else:
                if os.environ[x] == 'CHANGE ME':
                    logging.debug(f"Environment variable {x} not set - plugin be skipped")
                    ok = False
                else:
                    logging.debug(f"Environment variable {x} found")
                    data[x] = os.environ[x]
        if ok:
            return data
        else:
            return False
    
    # when setting 'index', the data is not deleted.  Any data record that matches the index is overwritten, and anything else is added
    # nothing gets deleted in this mode

    def store_df(self,tag,df):
        table_name = tag

        if not tag in self.row_count:
            self.row_count[tag] = 0
        self.row_count[tag] += len(df)
        logging.info(f"Storing dataframe {tag} - (total of {self.row_count[tag]} rows)")

        # -- add the fields required in every table
        df['tenancy'] = os.environ.get('TENANCY', 'default')
        df['upload_timestamp'] = pd.to_datetime(self.sync_time)

        # -- store the data in memory until we write it
        if not tag in self.df:
            self.df[tag] = pd.DataFrame()
        self.df[tag] = pd.concat([self.df[tag],df],ignore_index=True)

    def target_path(self,path,tag):
        VARS = {
            'YYYY'      : datetime.datetime.now(datetime.UTC).strftime('%Y'),
            'MM'        : datetime.datetime.now(datetime.UTC).strftime('%m'),
            'DD'        : datetime.datetime.now(datetime.UTC).strftime('%d'),
            'UUID'      : str(uuid.uuid4()),
            'TAG'       : tag,
            'TENANCY'   : os.environ.get('TENANCY','default')
        }
        
        for x in VARS:
            path = path.replace(f"${x}",VARS[x])
        return path
    
    def write_blank(self,tag,record):
        if self.row_count.get(tag,0) == 0:
            logging.info(f"{tag} - Writing a BLANK record")
    
            df = pd.DataFrame([ record ])
            self.store_df(tag,df)
            self.write_df(tag)
    
    def write_df(self,tag):
        # Get the data to upload
        data_to_upload = self.df.get(tag, pd.DataFrame())
        
        # Upload to PostgreSQL if available and has data
        if (self.postgres_uploader.is_available() and not data_to_upload.empty):
            try:
                self.postgres_uploader.upload_data(tag, data_to_upload)
            except Exception as e:
                logging.error(f"Failed to upload PostgreSQL data for tag '{tag}': {e}")
                self.write_errors.append(f"{tag} (postgres): {e}")

        # Upload to DuckDB if available and has data
        if (self.duckdb_uploader.is_available() and not data_to_upload.empty):
            try:
                self.duckdb_uploader.upload_data(tag, data_to_upload)
            except Exception as e:
                logging.error(f"Failed to upload DuckDB data for tag '{tag}': {e}")
                self.write_errors.append(f"{tag} (duckdb): {e}")

        # Upload to BigQuery if available and has data
        if (self.bigquery_uploader.is_available() and not data_to_upload.empty):
            try:
                self.bigquery_uploader.upload_data(tag, data_to_upload)
            except Exception as e:
                logging.error(f"Error uploading to BigQuery for tag '{tag}': {e}")
                self.write_errors.append(f"{tag} (bigquery): {e}")
        
        # Handle other file outputs only if self.df[tag] has data
        if tag in self.df and not self.df[tag].empty:
            if 'PARQUET_PATH' in os.environ:
                path = self.target_path(os.environ['PARQUET_PATH'],tag)
                logging.info(f"Writing Parquet file ({len(self.df[tag])}) : {path}")
                os.makedirs(os.path.dirname(path), exist_ok=True)
                try:
                    self.df[tag].to_parquet(path)
                    logging.info(f"SUCCESS writing Parquet : {path}")
                except Exception as e:
                    logging.error(f"ERROR writing Parquet : {e}")
                    self.write_errors.append(f"{tag} (parquet): {e}")

            # -- create local json file
            if 'UPLOAD_TARGET' in os.environ:
                path = self.target_path(os.environ['UPLOAD_TARGET'],tag)
                try:
                    os.makedirs(os.path.dirname(path),exist_ok = True)
                    self.df[tag].to_json(path, orient='records', lines=False, indent=2)
                    logging.info(f" - SUCCESS writing JSON : {path}")
                except Exception as e:
                    logging.error(f" - ERROR writing JSON : {e}")
                    self.write_errors.append(f"{tag} (json): {e}")

        # Clear the dataframe
        if tag in self.df:
            self.df[tag] = pd.DataFrame()

    def cleanup(self):
        """Clean up resources"""
        try:
            # Close PostgreSQL connection
            if hasattr(self, 'postgres_uploader'):
                self.postgres_uploader.close()
                
            # Close DuckDB connection
            if hasattr(self, 'duckdb_uploader'):
                self.duckdb_uploader.close()
                
            # Close BigQuery connection
            if hasattr(self, 'bigquery_uploader'):
                self.bigquery_uploader.close()
                
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")

class UploadBigQuery:
    """BigQuery uploader class"""
    
    def __init__(self, collector):
        self.collector = collector
        self.available = False
        self.client = None
        self.project_id = None
        self.dataset_id = None
        
        # Initialize BigQuery connection
        self.connect()
        
    def connect(self):
        """Connect to BigQuery"""
        try:
            from google.cloud import bigquery
            
            # Get configuration from environment
            self.project_id = os.environ.get('BQ_PROJECT_ID')
            self.dataset_id = os.environ.get('BQ_DATASET')
            bq_credentials = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
            
            if not self.project_id or not self.dataset_id:
                logging.info("BigQuery configuration not found, skipping initialization")
                return
            
            # Set up credentials if provided
            if bq_credentials:
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = bq_credentials
                
            self.client = bigquery.Client(project=self.project_id)
            self.available = True
            logging.info("BigQuery connection established successfully")
            
        except Exception as e:
            logging.error(f"Error connecting to BigQuery: {e}")
            self.available = False
            
    def upload_data(self, tag, df):
        """Upload data to BigQuery"""
        if not self.available or df.empty:
            return

        try:
            from google.cloud import bigquery

            table_name = tag
            table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"
            tenancy = df['tenancy'].iloc[0] if 'tenancy' in df.columns else os.environ.get('TENANCY', 'default')

            logging.info(f"Uploading {len(df)} rows to BigQuery table '{self.dataset_id}.{table_name}' for tenancy '{tenancy}'")

            # Delete existing rows for this tenant (no-op if table doesn't exist yet)
            try:
                delete_query = f"DELETE FROM `{table_id}` WHERE tenancy = @tenancy"
                delete_config = bigquery.QueryJobConfig(
                    query_parameters=[bigquery.ScalarQueryParameter("tenancy", "STRING", tenancy)]
                )
                self.client.query(delete_query, job_config=delete_config).result()
            except Exception:
                pass

            # Append new rows (creates table if it doesn't exist)
            job_config = bigquery.LoadJobConfig(
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
                autodetect=True
            )

            job = self.client.load_table_from_dataframe(df, table_id, job_config=job_config)
            job.result()

            logging.info(f"Successfully uploaded {len(df)} rows to BigQuery table '{self.dataset_id}.{table_name}'")
            
        except Exception as e:
            logging.error(f"Error uploading to BigQuery for tag '{tag}': {e}")
            
    def is_available(self):
        """Check if BigQuery configuration is available"""
        return self.available
            
    def close(self):
        """Close BigQuery connection"""
        if self.client:
            self.client.close()
            self.client = None
            logging.info("BigQuery connection closed")

class UploadPostgress:
    def __init__(self, collector):
        self.collector = collector
        self._engine = None
        self._schema_created = False
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
        
    @property
    def engine(self):
        """Create and return a singleton PostgreSQL engine with connection pooling"""
        if self._engine is None:
            try:
                connection_string = f"postgresql+psycopg://{os.environ['POSTGRES_USERNAME']}:{quote(os.environ['POSTGRES_PASSWORD'])}@{os.environ['POSTGRES_ENDPOINT']}:{os.environ.get('POSTGRES_PORT','5432')}/{os.environ['POSTGRES_DATABASE']}?options=-csearch_path%3D{os.environ.get('POSTGRES_SCHEMA','public')}"
                
                self._engine = create_engine(
                    connection_string, 
                    pool_pre_ping=True,
                    pool_size=10,
                    max_overflow=20,
                    pool_recycle=3600,
                    echo=False
                )
                
                # Test the connection
                with self._engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                    
                logging.info("PostgreSQL connection pool initialized successfully")
                
            except Exception as e:
                logging.critical(f"Failed to initialize PostgreSQL connection pool: {e}")
                raise
                
        return self._engine
    
    def ensure_schema_exists(self):
        """Ensure the PostgreSQL schema exists, create if it doesn't"""
        if not self._schema_created:
            try:
                schema = os.environ.get('POSTGRES_SCHEMA', 'public')
                with self.engine.connect() as conn:
                    conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
                    conn.commit()
                logging.info(f"PostgreSQL schema '{schema}' ensured to exist")
                self._schema_created = True
            except Exception as e:
                logging.error(f"Failed to create PostgreSQL schema: {e}")
                raise
    
    def upload_data(self, tag, df):
        """Upload DataFrame data using chunked approach"""
        if df.empty:
            logging.debug(f"No data to upload for PostgreSQL tag '{tag}'")
            return

        try:
            # Ensure schema exists
            self.ensure_schema_exists()

            table_name = tag
            schema = os.environ.get('POSTGRES_SCHEMA', 'public')
            tenancy = df['tenancy'].iloc[0] if 'tenancy' in df.columns else os.environ.get('TENANCY', 'default')

            logging.info(f"Uploading {len(df)} rows to PostgreSQL table '{table_name}' for tenancy '{tenancy}'")

            # Delete existing rows for this tenant (no-op if table doesn't exist yet)
            with self.engine.connect() as conn:
                try:
                    conn.execute(text(f'DELETE FROM "{schema}"."{table_name}" WHERE tenancy = :tenancy'), {'tenancy': tenancy})
                    conn.commit()
                except Exception:
                    conn.rollback()

            dtype_map = self._null_dtype_map(df)
            df.to_sql(
                table_name,
                self.engine,
                if_exists='append',
                index=False,
                schema=schema,
                method='multi',
                chunksize=1000,
                dtype=dtype_map if dtype_map else None,
            )

            logging.info(f"Successfully uploaded {len(df)} rows to PostgreSQL table '{table_name}'")

        except Exception as e:
            logging.error(f"Failed to upload data to PostgreSQL for tag '{tag}': {e}")
            raise

    def _null_dtype_map(self, df):
        from sqlalchemy import types as sa_types
        return {
            col: sa_types.NullType()
            for col in df.columns
            if df[col].dtype == object and df[col].isna().all()
        }
    
    def is_available(self):
        """Check if PostgreSQL configuration is available"""
        try:
            return all(key in os.environ for key in [
                'POSTGRES_USERNAME', 'POSTGRES_PASSWORD', 
                'POSTGRES_ENDPOINT', 'POSTGRES_DATABASE'
            ])
        except:
            return False
    
    def close(self):
        """Clean up resources"""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            logging.info("PostgreSQL connection pool closed")

class UploadDuckDB:
    def __init__(self, collector):
        self.collector = collector
        self._engine = None
        self._schema_created = False
        
    @property
    def engine(self):
        """Create and return a singleton DuckDB engine with connection pooling"""
        if self._engine is None:
            try:
                duckdb_file = os.environ['DUCKDB_FILE']
                self._engine = create_engine(
                    f'duckdb:///{duckdb_file}',
                    pool_pre_ping=True,
                    pool_size=5,
                    max_overflow=10,
                    pool_recycle=3600,
                    echo=False
                )
                
                # Test the connection
                with self._engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                    
                logging.info(f"DuckDB connection pool initialized successfully: {duckdb_file}")
                
            except Exception as e:
                logging.critical(f"Failed to initialize DuckDB connection pool: {e}")
                raise
                
        return self._engine
    
    def ensure_schema_exists(self):
        """Ensure the DuckDB schema exists, create if it doesn't"""
        if not self._schema_created:
            try:
                schema = os.environ.get('DUCKDB_SCHEMA', 'source')
                # Use native DuckDB connection for schema creation to avoid reflection warnings
                duckdb_file = os.environ['DUCKDB_FILE']
                with duckdb.connect(duckdb_file) as conn:
                    conn.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema}"')
                logging.info(f"DuckDB schema '{schema}' ensured to exist")
                self._schema_created = True
            except Exception as e:
                logging.error(f"Failed to create DuckDB schema: {e}")
                raise
    
    def upload_data(self, tag, df):
        """Upload DataFrame data using chunked approach"""
        if df.empty:
            logging.debug(f"No data to upload for DuckDB tag '{tag}'")
            return

        try:
            # Ensure schema exists
            self.ensure_schema_exists()

            table_name = tag
            schema = os.environ.get('DUCKDB_SCHEMA', 'source')
            tenancy = df['tenancy'].iloc[0] if 'tenancy' in df.columns else os.environ.get('TENANCY', 'default')

            logging.info(f"Uploading {len(df)} rows to DuckDB table '{table_name}' for tenancy '{tenancy}'")

            # Delete existing rows for this tenant (no-op if table doesn't exist yet)
            with self.engine.connect() as conn:
                try:
                    conn.execute(text(f'DELETE FROM "{schema}"."{table_name}" WHERE tenancy = :tenancy'), {'tenancy': tenancy})
                    conn.commit()
                except Exception:
                    conn.rollback()

            df.to_sql(
                table_name,
                self.engine,
                if_exists='append',
                index=False,
                schema=schema,
                method='multi',
                chunksize=1000
            )

            logging.info(f"Successfully uploaded {len(df)} rows to DuckDB table '{table_name}'")

        except Exception as e:
            logging.error(f"Failed to upload data to DuckDB for tag '{tag}': {e}")
            raise
    
    def is_available(self):
        """Check if DuckDB configuration is available"""
        try:
            return 'DUCKDB_FILE' in os.environ and os.environ['DUCKDB_FILE']
        except:
            return False
    
    def close(self):
        """Clean up resources"""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            logging.info("DuckDB connection pool closed")

if __name__=='__main__':
    load_dotenv('../.env')
    start_time = datetime.datetime.now()

    src = 'source'

    max_workers = int(os.environ.get('COLLECTOR_THREADS', 3))
    if 'DUCKDB_FILE' in os.environ and os.environ['DUCKDB_FILE']:
        if max_workers != 1:
            logging.warning("DuckDB does not support concurrent writes. Limiting to 1 thread regardless of COLLECTOR_THREADS.")
        max_workers = 1

    logging.info(f"Running collector with {max_workers} thread(s).")

    def run_plugin(p: str) -> tuple[str, str, str | None]:
        C = Collector()
        m = p.replace('.py', '')
        try:
            getattr(importlib.import_module(f"{src}.{m}"), "Source")(C)
            if C.write_errors:
                detail = "; ".join(C.write_errors)
                return m, "WRITE_FAILED", detail
            return m, "OK", None
        except Exception:
            return m, "FAILED", traceback.format_exc()
        finally:
            C.cleanup()

    plugins = sorted([f for f in os.listdir(src) if f.endswith('.py')])
    table_status = []
    alert_instance = Alert()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(run_plugin, p): p for p in plugins}
        for future in as_completed(futures):
            m, status, tb = future.result()
            table_status.append({"Module": m, "Status": status})
            if status == "FAILED":
                logging.error(f"Error running source: {m}\n{tb}")
                alert_instance.send(f"Error running source: {m}\n{tb}", "ERROR")
            elif status == "WRITE_FAILED":
                logging.error(f"Write error in source: {m}: {tb}")
                alert_instance.send(f"Write error in source: {m}: {tb}", "ERROR")

    table_status.sort(key=lambda x: x["Module"])
    counter_total = len(table_status)
    counter_ok = sum(1 for t in table_status if t["Status"] == "OK")
    counter_write_failed = sum(1 for t in table_status if t["Status"] == "WRITE_FAILED")

    time_elapsed = datetime.datetime.now() - start_time
    logging.info("------------------------------------------")
    for i in table_status:
        logging.info(f"{i['Module']:<20} - {i['Status']}")

    elapsed = int(time_elapsed.total_seconds())
    if counter_total == counter_ok:
        logging.info("SUCCESS")
        logging.info("------------------------------------------")
        alert_instance.send(f"Collector completed with {counter_ok} / {counter_total} - elapsed time {elapsed} seconds", "SUCCESS")
        exit(0)
    else:
        logging.fatal("FAILURE")
        logging.info("------------------------------------------")
        summary = f"Collector completed with {counter_ok} / {counter_total} ({counter_write_failed} write failure(s)) - elapsed time {elapsed} seconds"
        alert_instance.send(summary, "ERROR")
        exit(1)
