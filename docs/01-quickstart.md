# Quick start

The following steps will describe how to get the solution running on your local machine.

The quick start process will use a local [duckdb](https://duckdb.org) instance.

## Requirements

* You need to have Python 3.11 (or greater) installed
* Internet access (to reach the API endpoints)
* API keys for the data sources.

## Create a `.env` file

The solution is built around the use of environment variables.  API keys and database connection details are typically defined as environment variables.  The easiest way to achieve this, is by creating a `.env` file in the rot of the repository.

> [!CAUTION]
> The `.env` file will typically contain sensitive API keys and secrets.  If you're not keen to use a .env file, you can also deploy this using other mechanisms, as long as the environment variable is populated at the time of execution.

```
DOMAINS=mantelgroup.com.au
OKTA_TOKEN="xxx"
OKTA_DOMAIN="https://mantelgroup.okta.com"
FALCON_CLIENT_ID="xxx"
FALCON_SECRET="xxx"
KNOWBE4_TOKEN="xxx"
AZURE_TENANT_ID="xxx"
AZURE_CLIENT_ID="xxx"
AZURE_CLIENT_SECRET="xxx"
TENABLE_ACCESS_KEY="xxx"
TENABLE_SECRET_KEY="xxx"
```

## Kick things off

When your `.env` file is defined, you can run the `sh quickstart.sh` script.  It will do the following:
* create a virtual Python environment
* install all the required modules
* kick off the data collection process.
* kick off the data transformation process.
* Launch the dashboard.

### Access the website

Once the dashboard launches, you will be able to open the URL http://127.0.0.1:8050 to view the dashboard.
