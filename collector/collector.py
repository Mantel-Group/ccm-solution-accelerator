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
        
        # Upload to DuckDB if available and has data
        if (self.duckdb_uploader.is_available() and not data_to_upload.empty):
            try:
                self.duckdb_uploader.upload_data(tag, data_to_upload)
            except Exception as e:
                logging.error(f"Failed to upload DuckDB data for tag '{tag}': {e}")
        
        # Upload to BigQuery if available and has data
        if (self.bigquery_uploader.is_available() and not data_to_upload.empty):
            try:
                self.bigquery_uploader.upload_data(tag, data_to_upload)
            except Exception as e:
                logging.error(f"Failed to upload BigQuery data for tag '{tag}': {e}")
        
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

            # -- create local json file
            if 'UPLOAD_TARGET' in os.environ:
                path = self.target_path(os.environ['UPLOAD_TARGET'],tag)
                try:
                    os.makedirs(os.path.dirname(path),exist_ok = True)
                    self.df[tag].to_json(path, orient='records', lines=False, indent=2)
                    logging.info(f" - SUCCESS writing JSON : {path}")
                except Exception as e:
                    logging.error(f" - ERROR writing JSON : {e}")

        # Clear the dataframe
        if tag in self.df:
            self.df[tag] = pd.DataFrame()

    def xxxstore(self,tag,data):
        collection_duration = int((datetime.datetime.now() - self.collection_start).total_seconds())
        status = []

        dst = 'dest'
        tag = tag.lower().replace('.','_')

        if len(data) > 0:
            logging.info(f" DESTINATION of {tag} -- total of {len(data)} records")
            # -- loop through all plugins in the source folder
            for p  in sorted([f for f in os.listdir(dst) if f.endswith('.py')]):
                #logging.info(f"Destination plugin - {dst}/{p}")
                m = p.replace('.py','')
                try:
                    getattr(importlib.import_module(f"{dst}.{m}"),"Destination")(self,tag,data)
                    status.append({m : "SUCCESS"})
                except Exception as e:
                    logging.error(f"Error running destination : {m} - {e}")
                    status.append({m : "ERROR"})
        else:
            logging.warning(f" DESTINATION of {tag} -- No records to be written.. Will be skipped.")

        self.collection_start = datetime.datetime.now()

    def xxxdf_to_postgres(self,df,table,if_exists = 'replace'):
        try:
            # Connection string with proper URL encoding
            connection_string = f"postgresql+psycopg://{os.environ['POSTGRES_USERNAME']}:{quote(os.environ['POSTGRES_PASSWORD'])}@{os.environ['POSTGRES_ENDPOINT']}:{os.environ.get('POSTGRES_PORT','5432')}/{os.environ['POSTGRES_DATABASE']}?options=-csearch_path%3D{os.environ.get('POSTGRES_SCHEMA','public')}"

            try:
                engine = create_engine(connection_string, pool_pre_ping=True)
                engine.connect()  # Test connection
            except Exception as e:
                logging.critical(f"FAILED connecting to POSTGRES : {e}")
                sys.exit(1)

            with engine.connect() as conn:
                conn.execute(text("DEALLOCATE ALL"))    
            
            try:
                df.to_sql(table, engine, if_exists=if_exists, index=False,     schema=os.environ['POSTGRES_SCHEMA'])
                logging.info(" - SUCCESS writing POSTGRES")
            except Exception as e:
                logging.error(f" - ERROR writing POSTGRES : {e}")

        except Exception as e:
            logging.error(f" - ERROR Unexpected error during sync: {e}")
            sys.exit(1)

    def xxxdf_to_duckdb(self,df,table,if_exists = 'replace'):
        try:
            duckdb_file = os.environ['DUCKDB_FILE']
            duckdb_schema = os.environ.get('DUCKDB_SCHEMA','source')
            # duckdb:///<file> — three slashes if it's a relative path
            engine = create_engine(f'duckdb:///{duckdb_file}')
        except Exception as error:
            logging.critical(f"Unable to create DuckDB engine for: {duckdb_file} - {error}")
            sys.exit(1)

        try:
            df.to_sql(table, engine, if_exists=if_exists, index=False, schema=duckdb_schema)
            logging.info(" - SUCCESS writing DUCKDB")
        except Exception as e:
            logging.error(f" - ERROR writing DUCKDB : {e}")
            sys.exit(1)

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
            
            # Determine table name
            table_name = tag
            table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"
            
            logging.info(f"Uploading {len(df)} rows to BigQuery table '{self.dataset_id}.{table_name}'")
            
            # Configure the job
            job_config = bigquery.LoadJobConfig(
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
                autodetect=True
            )
            
            # Upload to BigQuery
            job = self.client.load_table_from_dataframe(df, table_id, job_config=job_config)
            job.result()  # Wait for the job to complete
            
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
            logging.info(f"Uploading {len(df)} rows to PostgreSQL table '{table_name}'")
            
            # Upload with chunking for better performance
            schema = os.environ.get('POSTGRES_SCHEMA', 'public')
            df.to_sql(
                table_name,
                self.engine,
                if_exists='replace',
                index=False,
                schema=schema,
                method='multi',  # Use multi-row inserts for better performance
                chunksize=1000   # Process in chunks of 1000 rows
            )
            
            logging.info(f"Successfully uploaded {len(df)} rows to PostgreSQL table '{table_name}'")
            
        except Exception as e:
            logging.error(f"Failed to upload data to PostgreSQL for tag '{tag}': {e}")
            raise
    
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
            logging.info(f"Uploading {len(df)} rows to DuckDB table '{table_name}'")
            
            # Upload with chunking for better performance
            schema = os.environ.get('DUCKDB_SCHEMA', 'source')
            df.to_sql(
                table_name,
                self.engine,
                if_exists='replace',
                index=False,
                schema=schema,
                method='multi',  # Use multi-row inserts for better performance
                chunksize=1000   # Process in chunks of 1000 rows
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
    C = Collector()
    start_time = datetime.datetime.now()

    src = 'source'

    counter = [ 0, 0]
    table_status = []

    # -- loop through all plugins in the source folder
    for p  in sorted([f for f in os.listdir(src) if f.endswith('.py')]):
        counter[0] += 1
        logging.info(f"Source plugin - {src}/{p}")

        m = p.replace('.py','')
        try:
            getattr(importlib.import_module(f"{src}.{m}"), "Source")(C)
            counter[1] += 1
            table_status.append({"Module": m, "Status": "OK"})
        except Exception as e:
            logging.error(f"Error running source: {m}\n{traceback.format_exc()}")
            C.alert.send(f"Error running source: {m}\n{traceback.format_exc()}", "ERROR")
            table_status.append({"Module": m, "Status": "FAILED"})

    time_elapsed = datetime.datetime.now() - start_time
    logging.info("------------------------------------------")
    for i in table_status:
        logging.info(f"{i['Module']:<20} - {i['Status']}")
    
    # Clean up and upload any remaining data
    C.cleanup()
    
    if counter[0] == counter[1]:
        logging.info("SUCCESS")
        logging.info("------------------------------------------")
        C.alert.send('Collector completed with {} / {} - elapsed time {} seconds'.format(counter[1],counter[0],int(time_elapsed.total_seconds())),'SUCCESS')
        exit(0)
    else:
        logging.fatal("FAILURE")
        logging.info("------------------------------------------")
        C.alert.send('Collector completed with {} / {} - elapsed time {} seconds'.format(counter[1],counter[0],int(time_elapsed.total_seconds())),'ERROR')
        exit(1)
