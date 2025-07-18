#!/bin/sh

if [ -f ../.env ]; then
    echo "We cannot run the test with a .env file in the mix"
    mv ../.env ../.env_orig
fi

export DUCKDB_FILE=../blank_file.duckdb
export DUCKDB_SCHEMA=source

export POSTGRES_ENDPOINT=localhost
export POSTGRES_DATABASE=postgres
export POSTGRES_USERNAME=postgres
export POSTGRES_PASSWORD=postgres
export POSTGRES_SCHEMA=source
export POSTGRES_PORT=5432

docker stop my-postgres
docker rm my-postgres
docker run --name my-postgres \
        -e POSTGRES_USER=$POSTGRES_USERNAME \
        -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
        -e POSTGRES_DB=$POSTGRES_DATABASE \
        -p $POSTGRES_PORT:$POSTGRES_PORT \
        -d postgres:17

if [ $? != 0 ]; then
    echo "ERROR  - something went wrong with the postgres container"
    exit 1
fi

echo "Wait some time for Postgres to fire up"
sleep 10

if [ -f $DUCKDB_FILE ]; then
    echo "Deleting duckdb file $DUCKDB_FILE"
    rm $DUCKDB_FILE
fi

unset DOMAINS
unset OKTA_TOKEN
unset OKTA_DOMAIN
unset FALCON_CLIENT_ID
unset FALCON_SECRET
unset KNOWBE4_TOKEN
unset AZURE_TENANT_ID
unset AZURE_CLIENT_ID
unset AZURE_CLIENT_SECRET
unset TENABLE_ACCESS_KEY
unset TENABLE_SECRET_KEY
unset BQ_PROJECT_ID
unset PARQUET_PATH
unset UPLOAD_TARGET
unset ALERT_SLACK_WEBHOOK

# == run the collector
cd ../collector
python3 collector.py

if [ $? != 0 ]; then
    echo "ERROR  - something went wrong with the collector"
    exit 1
fi

# == run the datapipeline
export POSTGRES_SCHEMA=public
cd ../datapipeline
dbt deps --target pg
dbt build --target pg
if [ $? != 0 ]; then
    echo "ERROR  - something went wrong with the postgres data pipeline"
    exit 1
fi

dbt deps --target duckdb
dbt build --target duckdb
if [ $? != 0 ]; then
    echo "ERROR  - something went wrong with the duckdb data pipeline"
    exit 1
fi