#!/bin/sh

if [ -f ../.env_orig ]; then
    echo "For a full test, we need the .env file ready"
    mv ../.env_orig ../.env
fi

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

export DUCKDB_FILE=../blank_file.duckdb
export DUCKDB_SCHEMA=source

if [ -f $DUCKDB_FILE ]; then
    echo "Deleting duckdb file $DUCKDB_FILE"
    rm $DUCKDB_FILE
fi

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
    echo "ERROR  - something went wrong with the data pipeline (postgres)"
    exit 1
fi


# == run the datapipeline
cd ../datapipeline
dbt deps --target duckdb
dbt build --target duckdb
if [ $? != 0 ]; then
    echo "ERROR  - something went wrong with the data pipeline"
    exit 1
fi