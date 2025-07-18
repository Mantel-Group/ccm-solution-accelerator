#!/bin/sh

# we assume you've got the Postgres docker instance already running

export POSTGRES_ENDPOINT=localhost
export POSTGRES_DATABASE=postgres
export POSTGRES_USERNAME=postgres
export POSTGRES_PASSWORD=postgres
export POSTGRES_SCHEMA=public
export POSTGRES_PORT=5432

unset DUCKDB_FILE
unset DUCKDB_SCHEMA

cd ../dashboard
python3 app.py
