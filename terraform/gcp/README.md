# GCP Terraform Configuration

This directory contains Terraform configuration files to deploy the Continuous Controls Monitoring (CCM) Dashboard infrastructure on Google Cloud Platform (GCP).

## Overview

This Terraform configuration deploys a complete CCM infrastructure on GCP including:

- **Cloud Run Services**: Containerised applications for data collection, processing, and dashboard
- **Cloud SQL**: PostgreSQL database for data storage
- **Cloud Scheduler**: Automated job scheduling for data collection and processing
- **Secret Manager**: Secure storage for API keys and credentials
- **Artifact Registry**: Container image storage
- **VPC & Networking**: Private networking with VPC connector
- **IAM**: Service accounts and permissions

## Architecture

The deployment creates three main components:

1. **Collector Job** (`ccm-{tenant}-collector`): Scheduled Cloud Run job that collects data from various security platforms (Okta, CrowdStrike, KnowBe4, Tenable, Azure Entra, etc.)
2. **Data Pipeline Job** (`ccm-{tenant}-datapipeline`): Scheduled Cloud Run job that processes and transforms collected data using dbt
3. **Dashboard Service** (`ccm-{tenant}-dashboard`): Always-running Cloud Run service providing a web interface for viewing security metrics

## Prerequisites

Before deploying, ensure you have:

1. **GCP Project**: A GCP project with billing enabled
2. **Terraform**: Terraform installed (version compatible with Google provider ~> 6.0)
3. **gcloud CLI**: Google Cloud CLI installed and authenticated
4. **Docker Images**: Container images built and pushed to Artifact Registry
5. **API Credentials**: Valid API tokens for the security platforms you want to integrate

### Required GCP APIs

The following APIs will be automatically enabled during deployment:
- Service Usage API
- Cloud Resource Manager API
- Identity and Access Management (IAM) API
- Compute Engine API
- Container Registry API
- Cloud Build API
- Cloud Run API
- Secret Manager API
- Artifact Registry API
- Cloud SQL Admin API
- VPC Access API
- Service Networking API

## Configuration

### Option 1: Using Examples Pattern (Recommended)

Navigate to the examples directory:
```bash
cd terraform/examples/gcp
```

Copy and edit the main configuration file:
```bash
cp main.tf.orig main.tf
```

Edit `main.tf` with your specific values:

```hcl
module "gcp" {
  source = "../../gcp"
  
  # Required Configuration
  gcp_project_id = "your-gcp-project-id"     # CHANGE ME
  region         = "australia-southeast1"    # CHANGE ME
  tenant         = "your-organization"       # CHANGE ME
  
  # Optional: Slack Alerting
  alert_slack_webhook = "https://hooks.slack.com/services/..."
  alert_slack_token   = "xoxb-your-slack-token"
  alert_slack_channel = "#security-alerts"
  
  # Optional: Resource Configuration
  container_cpu    = "1.0"
  container_memory = "2048"
  
  # Required: Resource Tags
  tags = {
    project     = "continuous-controls-monitoring-starter-template"
    owner       = "your-name"
    client      = "internal"
    domain      = "cyber"
    environment = "prod"
    tenant      = "your-organization"
  }
  
  # Required: API Credentials
  secrets = {
    FALCON_CLIENT_ID    = "your-crowdstrike-client-id"
    FALCON_SECRET       = "your-crowdstrike-secret"
    TENABLE_ACCESS_KEY  = "your-tenable-access-key"
    TENABLE_SECRET_KEY  = "your-tenable-secret-key"
    KNOWBE4_TOKEN       = "your-knowbe4-token"
    OKTA_TOKEN          = "your-okta-token"
    OKTA_DOMAIN         = "https://your-org.okta.com"
    AZURE_TENANT_ID     = "your-azure-tenant-id"
    AZURE_CLIENT_ID     = "your-azure-client-id"
    AZURE_CLIENT_SECRET = "your-azure-client-secret"
    DOMAINS             = "example.com,company.com"
  }
}
```

### Option 2: Direct Module Usage

Navigate to the GCP module directory:
```bash
cd terraform/gcp
```

Copy and edit the terraform variables file:
```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your specific values (see terraform.tfvars.example for full configuration options).

## Deployment

### Using Examples Pattern (Recommended)

```bash
cd terraform/examples/gcp
terraform init
terraform plan
terraform apply
```

### Using Direct Module

```bash
cd terraform/gcp
terraform init
terraform plan
terraform apply
```

## Post-Deployment

### 1. Access the Dashboard

The dashboard URL will be provided in the Terraform outputs:

```bash
terraform output dashboard_url
```

### 2. Manual Job Execution

You can manually trigger the data collection and processing jobs:

```bash
# Run collector job
gcloud run jobs execute ccm-{tenant}-collector --region={region} --project={project-id}

# Run datapipeline job  
gcloud run jobs execute ccm-{tenant}-datapipeline --region={region} --project={project-id}
```

### 3. Monitor Job Execution

- View job execution logs in the GCP Console under Cloud Run > Jobs
- Check Cloud Scheduler for automated job triggers
- Monitor database connections and performance in Cloud SQL

## File Structure

```
terraform/gcp/
├── README.md                    # This file
├── main.tf                      # Provider configuration
├── variables.tf                 # Variable definitions
├── terraform.tfvars.example    # Example configuration
├── outputs.tf                   # Output definitions
├── api_services.tf             # GCP API enablement
├── artifact_registry.tf        # Container registry
├── cloud_run.tf                # Cloud Run services and jobs
├── database.tf                 # Cloud SQL database
├── docker.tf                   # Docker image builds
├── networking.tf               # VPC and networking
├── scheduler.tf                # Cloud Scheduler jobs
└── secrets.tf                  # Secret Manager configuration
```

## Customisation

### Database Configuration

- **Instance Type**: Default is `db-f1-micro` (change `database_tier` variable)
- **PostgreSQL Version**: Default is `POSTGRES_14` (change `database_version` variable)
- **Public Access**: Disabled by default (change `database_public_access` variable)

### Resource Limits

Cloud Run services are configured with:
- **CPU**: 1000m (1 vCPU)
- **Memory**: 2Gi
- **Timeout**: 3 hours for jobs, default for dashboard service

### Scheduling

- **Collector**: Runs daily at 6:00 PM (configurable via `collector_cron_schedule`)
- **Data Pipeline**: Runs daily at 10:00 PM (configurable via `datapipeline_cron_schedule`)

## Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure your GCP account has sufficient permissions (Project Editor or specific IAM roles)
2. **API Not Enabled**: The configuration automatically enables required APIs, but manual enabling may be needed in some cases
3. **Container Images**: Ensure Docker images are built and pushed to Artifact Registry before deployment
4. **Quota Limits**: Check GCP quotas for Cloud Run, Cloud SQL, and other services

### Debugging

```bash
# Check Cloud Run job logs
gcloud logging read "resource.type=cloud_run_job" --project={project-id}

# Check database connectivity
gcloud sql connect {instance-name} --user={username} --project={project-id}

# View secret values (be careful with sensitive data)
gcloud secrets versions access latest --secret={secret-name} --project={project-id}
```

### Useful Commands

```bash
# List all Cloud Run services and jobs
gcloud run services list --region={region} --project={project-id}
gcloud run jobs list --region={region} --project={project-id}

# Check Cloud Scheduler jobs
gcloud scheduler jobs list --project={project-id}

# View Artifact Registry repositories
gcloud artifacts repositories list --project={project-id}
```

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

**Warning**: This will permanently delete all resources including the database and all stored data.

## Support

For issues related to:
- **Terraform Configuration**: Check the main project documentation
- **Application Issues**: Refer to the collector, datapipeline, and dashboard documentation
- **GCP Services**: Consult Google Cloud documentation

## Security Considerations

- All secrets are managed through Google Secret Manager
- Database is deployed in a private subnet with VPC connector
- Service accounts follow principle of least privilege
- Container images should be scanned for vulnerabilities
- Regular rotation of API keys and credentials is recommended
