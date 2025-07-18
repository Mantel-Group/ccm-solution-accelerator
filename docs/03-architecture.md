# Solution Architecture

The Terraform modules are build around a basic architecture that we'll describe below.  Regardless of what environment you run the solution, the basic application architecture will remain the same.

## Technical Architecture

* At the core of the solution is a **Postgres** database.  It is used for data colletion, processing.
* The **collector** job will connect to external API services, retrieve the data, and store it in the database.  The collector is controlled via environment variables, allowing to be turned into a docker container.
* Once collected, the **datapipeline** (`dbt`) performs the transformation.  It calculates the metrics, and creates tables to manage the historical nature of data (incremental models).  It also prepares data tables that can be consumed by the dashboard.
* The **dashboard** component is a Python Dash app that will connect to the database, to render the data.

## Auxility components

Since the dashboard is a Python Dash application, it is recommended to place the application behind an Nginx Reverse Proxy server.  Nginx will be used to control access to the application.

