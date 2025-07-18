import os
import time
import pandas as pd
from sqlalchemy import create_engine, text
import urllib.parse

class DatabaseQueryCache:
    def __init__(self, max_cache_age_minutes=60):
        # = is it Postgres or DuckDB?
        if os.getenv("POSTGRES_ENDPOINT"):
            print("Using Postgres database")
            endpoint = os.getenv("POSTGRES_ENDPOINT", "localhost")
            database = os.getenv("POSTGRES_DATABASE", "postgres")
            username = os.getenv("POSTGRES_USERNAME", "postgres")
            password = urllib.parse.quote(os.getenv("POSTGRES_PASSWORD", "postgres"))
            schema = os.getenv("POSTGRES_SCHEMA", "public")
            port = os.getenv("POSTGRES_PORT", "5432")
            
            print(f"Connecting to Postgres {endpoint}")

            # Build the SQLAlchemy database URL with schema
            # Note: schema can be set as 'options' in the URL or set in the connection session later
            # Using options here to set search_path to the desired schema
            db_url = (
                f"postgresql+psycopg://{username}:{password}@{endpoint}:{port}/{database}"
                f"?options=-csearch_path%3D{schema}"
            )
        elif os.getenv("DUCKDB_FILE"):
            print("Using DuckDB database")
            duckdb_file = os.getenv("DUCKDB_FILE", "data.duckdb")
            db_url = f"duckdb:///{duckdb_file}"
        else:
            raise ValueError("No database configuration found. Set either POSTGRES_ENDPOINT or DUCKDB_FILE environment variable.")

        self.engine = create_engine(db_url)
        self.max_cache_age = max_cache_age_minutes * 60  # seconds
        self.cache = {}

    def _cache_key(self, sql, params):
        params_tuple = tuple(sorted(params.items())) if params else ()
        return (sql, params_tuple)

    def query(self, sql, params=None):
        key = self._cache_key(sql, params or {})
        now = time.time()

        if key in self.cache:
            timestamp, df = self.cache[key]
            if (now - timestamp) < self.max_cache_age:
                return df

        with self.engine.connect() as conn:
            df = pd.read_sql(text(sql), conn, params=params)

        self.cache[key] = (now, df)
        return df
