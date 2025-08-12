# Continuous Controls Monitoring Solution Accelerator

## What is the CCM Solution Accelerator?

In today's dynamic threat landscape, organizations face significant challenges in rapidly understanding and reporting on their cyber security posture. Traditional methods often involve complex, time-consuming data aggregation and manual reporting, leading to delayed insights and reactive security measures.

Our Continuous Controls Monitoring (CCM) Dashboard provides a powerful, streamlined solution to this critical need. This innovative software is designed to deliver immediate, actionable insights into your cyber security controls, enabling proactive risk management and enhanced compliance.

**Key Features and Benefits:**

* **Effortless Data Integration:** The solution includes a robust data collection component capable of seamlessly retrieving crucial cyber security data from a diverse range of sources.
* **Intelligent Data Transformation:** Leveraging dbt (data build tool), our integrated ETL (Extract, Transform, Load) component transforms raw security data into a comprehensive suite of vital cyber metrics, ensuring data quality and relevance.
* **Instant Insights with Embedded Dashboard:** Gain immediate visibility through an intuitive, out-of-the-box dashboard embedded directly within the solution, eliminating the need for separate reporting tools.
* **Rapid Deployment & Value:** Designed for quick deployment, the CCM Dashboard allows organizations to establish a sophisticated cyber security reporting platform with minimal setup. Simply provide your API keys, and begin unlocking critical insights within minutes.

By automating data collection, transformation, and reporting, our CCM Dashboard empowers executives and security teams with real-time visibility into their cyber security performance, facilitating informed decision-making and a stronger defense against evolving threats.

> [!TIP]
> Just want to do a quick test on your local machine to see what it's all about?  Look at our [quick start](docs/01-quickstart.md) guide!

## What do you get?

* `collector` - the Docker instance to download source data
* `datapipeline` - the Docker instance with the dbt job to generate the metics
* `dashboard` - The basic Python Dash dashboard
* `terraform` - The terraform infrastructure deployer

## Other documentation

* Configuring [Azure Credentials](docs/creds_azure_entra.md)
* Running [Terraform](docs/02-terraform.md)
* [Solution Architecture](docs/03-architecture.md)
* Deploying to [Production](docs/04-production.md)
* [Metrics Library](docs/metric_library.md)
* [Attribution](docs/attribution.md)

## Supported database platforms

| Database   | Collector | Data Pipeline | Dashboard |
|------------|-----------|---------------|-----------|
| `postgres` | ✅         | ✅            | ✅        |
| `BigQuery` | ✅         | ✅            | ❌        |
| `DuckDB`   | ✅         | ✅            | ✅        |

The following environment variables are used to control the database

| Attribute       | postgres            | DuckDB          | BigQuery        |
|-----------------|---------------------|-----------------|-----------------|
| Server address  | `POSTGRES_ENDPOINT` | `DUCKDB_FILE`   |                 |
| Server port     | `POSTGRES_PORT`     |                 |                 |
| Database name   | `POSTGRES_DATABASE` |                 | `BQ_PROJECT_ID` |
| Database schema | `POSTGRES_SCHEMA`   | `DUCKDB_SCHEMA` | `BQ_DATASET`    |
| Username        | `POSTGRES_USERNAME` |                 |                 |
| Password        | `POSTGRES_PASSWORD` |                 |                 |

## Deployment Options

There are two options to deploy the solution:
* [Local Deployment](docs/01-quickstart.md)
* [Cloud (AWs/Azure/GCP) via Terraform](docs/02-terraform.md)

## Licensing

The Solution Accelerator is distributed under the [GNU General Public License v3.0
](https://choosealicense.com/licenses/gpl-3.0/#) license.

    Mantel Continuous Controls Monitoring Solution Accelerator
    Copyright (C) 2025  Mantel

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.