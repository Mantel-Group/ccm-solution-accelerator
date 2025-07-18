# Cloud deployment with Terraform

The Terraform modules are provided to install the Continuous Control Monitoring template on either AWS, Azure, or GCP.

## Preparing your cloud environment

In the `terraform/examples/{provider}` folder, there is a `main.tf.orig` file for each of the cloud platforms.  It is recommended that you **copy** this file, and create `main.tf`, and edit it.

### Common Requirements

For this solution to work, you will need to have the following components installed.

* Terraform
* Docker (or Colima on MacOS) - required to build the Docker images
* Cloud SDK for the cloud you are running from

## Cloud Provider Setup

### AWS

#### Networking

The AWS platform requires a VPC and subnets to already exist.  It is important that these subnets are internet-routable, as the containers will need to connect to the VPC endpoints to retrieve the images and SSM parameters (secrets).  It also requires (at least) NAT routing in order to reach the external API endpoints.

The containers are configured with Public IP addresses enabled.  It can however work with private addresses.  This is a manual change you can apply to the Terraform module.

#### Pre-requisites

* You need to have access to an AWS account.
* Log in to the AWS account with the AWS CLI, and be sure to set the `AWS_PROFILE` environment variable.
* Run `aws sts get-caller-identity` to confirm you are logged on successfully.
* Edit your `main.tf` file, and update any variables that require updating.
* You will need to provide the `vpc_id`, and `subnet_ids` where the database and containers will run from.
* The container subnets must be able to reach the internet.

### Azure

#### Networking

The Azure module will create the network for you, based on the CIDR ranges you provide, due to additional permissions required on each subnet.

#### Database

The Azure Postgres database cannot be made public, due to the way the Vnets are configured.

#### Pre-requisites
* You need to have access to an Azure Subscription.
* You will need the `subscription_id`.
* Edit your `main.tf` file, and update the `azure_subscription_id` to use.
* The Azure module will create a resource group, a Vnet, and all required subnets.
* You can provide the CIDRs if they need to fit into a specific scheme.
* Make sure you have run `az login` to log on before you continue.

### GCP

#### Networking

The GCP module will create a complete VPC network infrastructure for you, including:
- **VPC Network**: A regional VPC with custom subnets
- **Database Subnet**: Private subnet for Cloud SQL PostgreSQL instance
- **Container Subnet**: Subnet for Cloud Run services and jobs
- **VPC Connector**: Enables private connectivity between Cloud Run and Cloud SQL
- **Firewall Rules**: Configured to allow necessary traffic for dashboard access
- **Private Service Connect**: For secure database connections

The database is deployed privately by default and cannot be accessed from the internet. All communication between components uses private networking.

#### Database

The GCP PostgreSQL database (Cloud SQL) is deployed in a private subnet and cannot be made public due to the VPC configuration. All database access is through the VPC connector from Cloud Run services.

#### Pre-requisites

* You need to have access to a GCP Project with **Billing enabled**
* You will need the `gcp_project_id` from your GCP Console
* Install and authenticate the Google Cloud CLI:
  ```bash
  # Install gcloud CLI (if not already installed)
  # Follow instructions at: https://cloud.google.com/sdk/docs/install
  
  # Authenticate
  gcloud auth login
  
  # Set your default project
  gcloud config set project YOUR_PROJECT_ID
  
  # Enable required APIs (optional - Terraform will do this automatically)
  gcloud services enable run.googleapis.com
  gcloud services enable sqladmin.googleapis.com
  gcloud services enable secretmanager.googleapis.com
  ```
* You can provide custom CIDR ranges if they need to fit into a specific network scheme
* Edit your `main.tf` file in the `terraform/examples/gcp/` folder and update the `gcp_project_id`
* Ensure Docker is running (required to build container images):
  ```bash
  # On macOS with Colima
  colima start
  
  # Or with Docker Desktop
  docker --version
  ```

#### Container Images

The GCP deployment automatically builds and pushes three container images to Google Artifact Registry:
- **Collector**: Data collection from security platforms
- **Data Pipeline**: dbt-based data transformation
- **Dashboard**: Python Dash web interface

These images are built during the Terraform deployment process.

#### Authentication Setup

Configure Docker to authenticate with Google Artifact Registry:
```bash
gcloud auth configure-docker australia-southeast1-docker.pkg.dev --quiet
```

#### Resource Configuration

The GCP module creates:
- **Cloud Run Jobs**: For scheduled data collection and processing
- **Cloud Run Service**: For the always-running dashboard
- **Cloud SQL**: PostgreSQL database instance
- **Cloud Scheduler**: Automated job scheduling
- **Secret Manager**: Secure storage for API keys
- **Artifact Registry**: Container image storage
- **VPC Network**: Private networking infrastructure

#### Default Configuration

| Component | Default Setting | Customizable |
|-----------|----------------|--------------|
| Region | `australia-southeast1` | Yes |
| Database Version | `POSTGRES_14` | Yes |
| Database Instance | `db-f1-micro` | Yes |
| Container CPU | `1.0` vCPU | Yes |
| Container Memory | `2Gi` | Yes |
| VPC CIDR | `10.0.0.0/16` | Yes |
| Collector Schedule | Daily at 6:00 PM UTC | Yes |
| Data Pipeline Schedule | Daily at 10:00 PM UTC | Yes |

#### Quick Deployment Guide

1. **Navigate to the GCP examples folder:**
   ```bash
   cd terraform/examples/gcp
   ```

2. **Copy the example configuration:**
   ```bash
   cp main.tf.orig main.tf
   ```

3. **Edit the configuration:**
   ```bash
   # Update main.tf with your specific values:
   # - gcp_project_id: Your GCP project ID
   # - region: Your preferred region
   # - tenant: Your organization identifier
   # - secrets: Your API keys (see API keys section below)
   ```

4. **Deploy the infrastructure:**
   ```bash
   terraform init
   terraform plan    # Review the planned changes
   terraform apply   # Type 'yes' to confirm
   ```

5. **Initial setup (first time only):**
   ```bash
   # Get the manual trigger commands from Terraform outputs
   terraform output collector_job_trigger_command
   terraform output datapipeline_job_trigger_command
   
   # Run the collector job
   gcloud run jobs execute ccm-{tenant}-collector --region={region} --project={project-id}
   
   # After collector finishes, run the data pipeline
   gcloud run jobs execute ccm-{tenant}-datapipeline --region={region} --project={project-id}
   
   # Access the dashboard
   terraform output dashboard_url
   ```

#### Troubleshooting

Common issues and solutions:

- **Permission Errors**: Ensure your account has Project Editor role or specific IAM roles for the services being used
- **Billing Not Enabled**: Enable billing in the GCP Console for your project
- **Docker Not Running**: Start Docker/Colima before running Terraform
- **API Not Enabled**: Terraform automatically enables required APIs, but this may take a few minutes
- **Container Build Failures**: Check Docker daemon is running and you have sufficient disk space

For detailed logs:
```bash
# View Cloud Run job logs
gcloud logging read "resource.type=cloud_run_job" --project={project-id} --limit=50

# Check Cloud Scheduler status
gcloud scheduler jobs list --project={project-id}
```
## Provide your API keys

You will need to generate read-only credentials (API keys) to allow the collector to connect to the data sources.  Prepare the API keys in a text file as follow.

```
secrets = {
    FALCON_CLIENT_ID    = "CHANGE ME"
    FALCON_SECRET       = "CHANGE ME"
    TENABLE_ACCESS_KEY  = "CHANGE ME"
    TENABLE_SECRET_KEY  = "CHANGE ME"
    KNOWBE4_TOKEN       = "CHANGE ME"
    OKTA_TOKEN          = "CHANGE ME"
    OKTA_DOMAIN         = "CHANGE ME"
    AZURE_TENANT_ID     = "CHANGE ME"
    AZURE_CLIENT_ID     = "CHANGE ME"
    AZURE_CLIENT_SECRET = "CHANGE ME"
    DOMAINS             = "CHANGE ME"
  }
```

### Variables

| Variable | Required | Purpose | Default Value |
|----------|----------|---------|---------------|
| tenant | | Tenant/environment identifier | default |
| region | | Cloud region to use | Azure: australiaeast, AWS: ap-southeast-2 |
| azure_subscription_id | Yes | Azure Subscription ID | - |
| azure_resource_group_name | Yes | Azure Resource Group name | - |
| tags | | Tags to apply to resources | {"Project": "Continuous Controls Monitoring Starter Template"} |
| dashboard_cidr_inbound_allow | | Dashboard access CIDR | ["0.0.0.0/0"] |
| dashboard_username | | Default username for the dashboard | admin |
| dashboard_password | | Default password for the dashboard | s3cretW0rd |
| aws_vpc_id | Yes | AWS VPC ID | - |
| azure_vnet_cidr | | Virtual Network address space | ["10.0.0.0/16"] |
| gcp_vpc_cidr | | Virtual Network address space | ["10.0.0.0/16"] |
| aws_container_subnets | Yes | Subnet IDs for containers | - |
| aws_rds_subnet_ids | Yes | Subnet IDs for database | - |
| azure_subnet_container_cidr | | Container Apps subnet CIDR | ["10.0.0.0/21"] |
| gcp_container_subnet_cidr | | Container Apps subnet CIDR | ["10.0.0.0/21"] |
| azure_subnet_database_cidr | | Database subnet CIDR | ["10.0.8.0/24"] |
| gcp_database_subnet_cidr | | Database subnet CIDR | ["10.0.8.0/24"] |
| db_name | | Database name | Azure: continuous_assurance, AWS: CCM |
| db_username | | Database admin username | ContinuousAssurance |
| db_version | | Database version to use | Azure : 16, AWS: 17.4 |
| db_storage | | Database storage size (GB) | Azure: 32, AWS: 20 |
| db_public_facing | | Make database publicly accessible | false |
| db_cidr_inbound_allow | | Allowed CIDR ranges for database | [] |
| db_instance_size | | Database instance size | Azure: B_Standard_B1ms, AWS: db.t4g.micro |
| container_cpu | | CPU units for containers | 1024 |
| container_memory | | Memory for containers (MiB) | 2048 |
| cron_schedule | | Job scheduling cron expression | Azure: 0 18 * * *, AWS: 0 18 * * ? * |
| alert_slack_webhook | | Slack webhook for alerts | "" |
| alert_slack_token | | Slack token | "" |
| alert_slack_channel | | Slack alert channel | "" |
| secrets | Yes | API keys and sensitive configurations | Predefined map with placeholders |

## Deploy

In the `examples/{platform}` folder of your choice, run 

```bash
$ terraform init
$ terraform plan
$ terraform apply
```

## Using the solution

Terraform outputs have been configured that will provide some much needed information.  The following outputs will be provided when the module has completed running.

| Variable                           | What it is used for                                                   |
|------------------------------------|-----------------------------------------------------------------------|
| `collector_job_trigger_command`    | A command line command you can run to trigger the collector job       |
| `datapipeline_job_trigger_command` | A command line command you can run to trigger the datapipeline job    |
| `dashboard_url`                    | The fully qualified domain name of the dashboard you need to access   |
| `database`                         | The name of the database (if you choose to use a public interface)    |
| `database_server_fqdn`             | The database server address (if you choose to use a public interface) |
| `database_username`                | The database username  (if you choose to use a public interface)      |

The first time the solution boots up, it will not have had the opportunity to do a full run, so the dashboard will not operate correctly.  You can wait for 24 hours, and try again, or, you can run the following commands.

* Kick off the collector job using the command provided to you in Terraform : `collector_job_trigger_command` 
* Once that job finishes, run the datapipe command provided to you in Terraform : `datapipeline_job_trigger_command`
* Upon completion, you can view the website at the URL provided in the `dashboard_url` attribute in Terraform.

## Post-deployment

### Login

Use the `dashboard_username` and `dashboard_password` provided in the table above to login to the dashboard.

### AWS 

#### Find the dashboard IP

The Dashboard container is hosted as a Fargate task.  Since the task can run on a random IP address, a Lambda function has been provided to help you find the IP.  Use the Lambda Function URL as the dashboard URL, and a redirect will point you to the Fargate task.

To disable the use of the Lambda function, simply remove the `lambda.tf` file from the AWS folder, and redeploy.

You can also use an Application Load Balancer.  A simple change (enable `alb.tf` and disable `lambda.tf`) will allow the load balancer to be created, which will retain the same URL.
