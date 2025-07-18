# Dashboard URL output:
output "dashboard_url" {
  description = "Dashboard URL"
  value       = google_cloud_run_v2_service.dashboard.uri
}

output "database_server_fqdn" {
  description = "Database server"
  value       = google_sql_database_instance.database.public_ip_address
}

output "database_username" {
  description = "Database username"
  value       = google_sql_user.database_user.name
}

output "database" {
  description = "Database name"
  value       = google_sql_database.database.name
}

# Output database connection info (using dynamic references)
output "database_connection_info" {
  description = "Database connection information"
  value = {
    host     = google_sql_database_instance.database.public_ip_address
    port     = "5432"
    database = google_sql_database.database.name
    username = google_sql_user.database_user.name
  }
  sensitive = true
}


# Output collector job name
output "collector_job_name" {
  description = "Name of the collector Cloud Run job"
  value       = google_cloud_run_v2_job.collector.name
}

# Output datapipeline job name  
output "datapipeline_job_name" {
  description = "Name of the datapipeline Cloud Run job"
  value       = google_cloud_run_v2_job.datapipeline.name
}

# Output project and region info
output "deployment_info" {
  description = "Deployment information"
  value = {
    project_id = var.gcp_project_id
    region     = var.region
    tenant     = var.tenant
  }
}

# Output commands to run jobs manually
output "manual_job_commands" {
  description = "Commands to manually execute the jobs"
  value = {
    collector_command    = "gcloud run jobs execute ${google_cloud_run_v2_job.collector.name} --region=${var.region} --project=${var.gcp_project_id}"
    datapipeline_command = "gcloud run jobs execute ${google_cloud_run_v2_job.datapipeline.name} --region=${var.region} --project=${var.gcp_project_id}"
  }
}

# Output artifact registry URL
output "artifact_registry_url" {
  description = "Artifact Registry URL for pushing images"
  value       = "${var.region}-docker.pkg.dev/${var.gcp_project_id}/${local.artifact_registry_name}"
}

# Output service account email
output "cloud_run_service_account" {
  description = "Cloud Run service account email"
  value       = google_service_account.cloud_run_sa.email
}

output "db_password" {
  description = "Database password"
  value       = random_password.db_master.result
  sensitive   = true
}

# Output network information
output "network_info" {
  description = "Network and subnet information"
  value = {
    vpc_name              = google_compute_network.vpc.name
    vpc_id                = google_compute_network.vpc.id
    database_subnet_name  = google_compute_subnetwork.database_subnet.name
    database_subnet_cidr  = google_compute_subnetwork.database_subnet.ip_cidr_range
    container_subnet_name = google_compute_subnetwork.container_subnet.name
    container_subnet_cidr = google_compute_subnetwork.container_subnet.ip_cidr_range
    vpc_connector_name    = google_vpc_access_connector.connector.name
  }
}
