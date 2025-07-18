#!/bin/sh

set -e

PY=python3

echo "== Setup the new environment"
if [ -f myenv ]; then
    echo Deleting old environment
    rm -rf myenv
fi

$PY -m venv myenv
source myenv/bin/activate

$PY -m pip install -r ./collector/requirements.txt
$PY -m pip install -r ./datapipeline/requirements.txt
$PY -m pip install -r ./dashboard/requirements.txt

# == we will be running the quick start on a DuckDB database
export DUCKDB_FILE=../data.duckdb
export DUCKDB_SCHEMA=source

# == if you want a clean database, uncomment this section
if [ -f $DUCKDB_FILE ]; then
    echo "Deleting duckdb file $DUCKDB_FILE"
    rm $DUCKDB_FILE
fi

# == We will only be testing the domains - keep it simple.  You can edit the ../.env file, or add some other variables hre
export DOMAINS=mantelgroup.com.au,mantelgroup.co.nz,mantelgroup.co.vn,mantelconnect.com,api-keys.ai.mantelgroup.com.au,ai.mantelgroup.com.au

cd collector
$PY collector.py

# == run the datapipeline
export DUCKDB_SCHEMA=public
cd ../datapipeline
dbt deps --target duckdb
dbt build --target duckdb

# == Run the dashboard - when complete, open http://localhost:8051
cd ../dashboard
export PORT=8051
python3 app.py