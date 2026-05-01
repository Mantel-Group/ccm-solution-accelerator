# Solution Architecture

The Terraform modules are build around a basic architecture that we'll describe below.  Regardless of what environment you run the solution, the basic application architecture will remain the same.

## Technical Architecture

* At the core of the solution is a **Postgres** database.  It is used for data colletion, processing.
* The **collector** job will connect to external API services, retrieve the data, and store it in the database.  The collector is controlled via environment variables, allowing to be turned into a docker container.
* Once collected, the **datapipeline** (`dbt`) performs the transformation.  It calculates the metrics, and creates tables to manage the historical nature of data (incremental models).  It also prepares data tables that can be consumed by the dashboard.
* The **dashboard** component is a Python Streamlit app that will connect to the database, to render the data.

## Multi-Tenant Support

The collector supports running multiple instances of the same collector (e.g. two CrowdStrike tenants) against a shared database without data loss. Each collector run is tagged with a `tenancy` value set via the `TENANCY` environment variable (defaults to `default`).

On each run the collector:
1. Deletes only the rows belonging to the current `tenancy` in the target table.
2. Inserts the freshly collected rows for that `tenancy`.

Other tenants' rows are left untouched. This means you can schedule two independent collector jobs with `TENANCY=tenant-a` and `TENANCY=tenant-b` and both will coexist in the same tables.

## Auxility components

Since the dashboard is a Streamlit application, it is recommended to place the application behind an Nginx Reverse Proxy server.  Nginx will be used to control access to the application.

