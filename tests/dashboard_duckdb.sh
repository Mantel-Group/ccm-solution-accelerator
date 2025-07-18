#!/bin/sh

# we assume you've got the Postgres docker instance already running

unset POSTGRES_ENDPOINT
unset POSTGRES_DATABASE
unset POSTGRES_USERNAME
unset POSTGRES_PASSWORD
unset POSTGRES_SCHEMA
unset POSTGRES_PORT

export DUCKDB_FILE=../blank_file.duckdb
export DUCKDB_SCHEMA=public

cd ../dashboard
python3 app.py
