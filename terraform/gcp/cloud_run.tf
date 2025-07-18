# Local values for common configurations
locals {
  # Common resource limits for all services - now using variables
  resource_limits = {
    cpu    = var.container_cpu
    memory = "${var.container_memory / 1024}Gi"
  }

  # Common database environment variables
  db_env_vars = {
    POSTGRES_ENDPOINT = google_sql_database_instance.database.private_ip_address
    POSTGRES_USERNAME = google_sql_user.database_user.name
    POSTGRES_DATABASE = google_sql_database.database.name
    POSTGRES_PORT     = "5432"
    _TENANT           = var.tenant
  }

  # Common Slack environment variables for all 3 containers
  slack_env_vars = {
    ALERT_SLACK_WEBHOOK = var.alert_slack_webhook
    ALERT_SLACK_TOKEN   = var.alert_slack_token
    ALERT_SLACK_CHANNEL = var.alert_slack_channel
  }

  # Secret references for environment variables
  secret_env_vars = {
    POSTGRES_PASSWORD = {
      secret  = google_secret_manager_secret.db_password.secret_id
      version = "latest"
    }
  }

  # All secrets that need IAM bindings for the service account - now dynamic
  secrets_for_binding = merge(
    {
      db_password   = google_secret_manager_secret.db_password.secret_id
      db_connection = google_secret_manager_secret.db_connection.secret_id
    },
    {
      for key, _ in var.secrets : lower(replace(key, "_", "-")) => google_secret_manager_secret.api_secrets[key].secret_id
    }
  )

  # Dynamic API secrets from variables - similar to AWS/Azure pattern
  api_secrets_env_vars = {
    for key, _ in var.secrets : key => {
      secret  = google_secret_manager_secret.api_secrets[key].secret_id
      version = "latest"
    }
  }

  # Service account IAM roles
  service_account_roles = [
    "roles/cloudsql.client",
    "roles/cloudsql.editor"
  ]
}

# Service Account for Cloud Run services
resource "google_service_account" "cloud_run_sa" {
  account_id   = "ccm-${var.tenant}-runner"
  display_name = "Cloud Run Service Account for ${var.tenant}"
  description  = "Service account for continuous assurance Cloud Run services"
  depends_on   = [time_sleep.all_apis_ready]
}

# Consolidated IAM bindings for Secret Manager access using for_each
resource "google_secret_manager_secret_iam_binding" "secret_bindings" {
  for_each = local.secrets_for_binding

  project    = var.gcp_project_id
  secret_id  = each.value
  role       = "roles/secretmanager.secretAccessor"
  members    = ["serviceAccount:${google_service_account.cloud_run_sa.email}"]
  depends_on = [time_sleep.all_apis_ready]
}

# Consolidated database access permissions using for_each
resource "google_project_iam_member" "cloud_run_permissions" {
  for_each = toset(local.service_account_roles)

  project    = var.gcp_project_id
  role       = each.value
  member     = "serviceAccount:${google_service_account.cloud_run_sa.email}"
  depends_on = [time_sleep.all_apis_ready]
}

# Cloud Run JOB for Collector (periodic data collection)
resource "google_cloud_run_v2_job" "collector" {
  name     = "ccm-${var.tenant}-collector"
  location = var.region

  depends_on = [
    null_resource.build_collector,
    google_project_service.run,
    google_project_service.secretmanager,
    google_secret_manager_secret_iam_binding.secret_bindings,
    google_project_iam_member.cloud_run_permissions,
    google_secret_manager_secret_version.db_connection,
    time_sleep.all_apis_ready
  ]
  deletion_protection = false

  template {
    template {
      timeout         = "10800s" # 3 hours
      service_account = google_service_account.cloud_run_sa.email
      max_retries     = 0

      vpc_access {
        connector = google_vpc_access_connector.connector.id
        egress    = "PRIVATE_RANGES_ONLY"
      }

      containers {
        image = "${var.region}-docker.pkg.dev/${var.gcp_project_id}/${local.artifact_registry_name}/collector:latest"

        resources {
          limits = local.resource_limits
        }

        # Common database environment variables
        dynamic "env" {
          for_each = local.db_env_vars
          content {
            name  = env.key
            value = env.value
          }
        }

        # Common Slack environment variables
        dynamic "env" {
          for_each = local.slack_env_vars
          content {
            name  = env.key
            value = env.value
          }
        }

        # Secret-based environment variables
        dynamic "env" {
          for_each = local.secret_env_vars
          content {
            name = env.key
            value_source {
              secret_key_ref {
                secret  = env.value.secret
                version = env.value.version
              }
            }
          }
        }

        # Collector-specific environment variables
        env {
          name  = "POSTGRES_SCHEMA"
          value = "source"
        }

        env {
          name = "_TRIGGER_REBUILD"
          value = md5(join("", [
            for f in fileset("${path.module}/../../collector", "**/*") : filemd5("${path.module}/../../collector/${f}")
          ]))
        }

        # Pre-built database connection string from secrets manager
        env {
          name = "DATABASE_URL"
          value_source {
            secret_key_ref {
              secret  = google_secret_manager_secret.db_connection.secret_id
              version = "latest"
            }
          }
        }

        # Dynamic API secrets from variables
        dynamic "env" {
          for_each = local.api_secrets_env_vars
          content {
            name = env.key
            value_source {
              secret_key_ref {
                secret  = env.value.secret
                version = env.value.version
              }
            }
          }
        }
      }
    }
  }
}

# Cloud Run JOB for Data Pipeline (periodic data processing and transformation)
resource "google_cloud_run_v2_job" "datapipeline" {
  name     = "ccm-${var.tenant}-datapipeline"
  location = var.region

  depends_on = [
    null_resource.build_datapipeline,
    google_project_service.run,
    google_project_service.secretmanager,
    google_secret_manager_secret_iam_binding.secret_bindings,
    google_project_iam_member.cloud_run_permissions,
    time_sleep.all_apis_ready
  ]
  deletion_protection = false

  template {
    template {
      timeout         = "900s" # 15 minutes
      service_account = google_service_account.cloud_run_sa.email
      max_retries     = 0

      vpc_access {
        connector = google_vpc_access_connector.connector.id
        egress    = "PRIVATE_RANGES_ONLY"
      }

      containers {
        image = "${var.region}-docker.pkg.dev/${var.gcp_project_id}/${local.artifact_registry_name}/datapipeline:latest"

        resources {
          limits = local.resource_limits
        }

        # Common database environment variables
        dynamic "env" {
          for_each = local.db_env_vars
          content {
            name  = env.key
            value = env.value
          }
        }

        # Common Slack environment variables
        dynamic "env" {
          for_each = local.slack_env_vars
          content {
            name  = env.key
            value = env.value
          }
        }

        # Secret-based environment variables
        dynamic "env" {
          for_each = local.secret_env_vars
          content {
            name = env.key
            value_source {
              secret_key_ref {
                secret  = env.value.secret
                version = env.value.version
              }
            }
          }
        }

        # Datapipeline-specific environment variables
        env {
          name  = "POSTGRES_SCHEMA"
          value = "public"
        }

        env {
          name = "_TRIGGER_REBUILD"
          value = md5(join("", [
            for f in fileset("${path.module}/../../datapipeline", "**/*") : filemd5("${path.module}/../../datapipeline/${f}")
          ]))
        }
      }
    }
  }
}

# Cloud Run SERVICE for Dashboard (always running web interface)
resource "google_cloud_run_v2_service" "dashboard" {
  name     = "ccm-${var.tenant}-dashboard"
  location = var.region

  depends_on = [
    null_resource.build_dashboard,
    google_project_service.run,
    google_project_service.secretmanager,
    google_secret_manager_secret_iam_binding.secret_bindings,
    google_project_iam_member.cloud_run_permissions,
    time_sleep.all_apis_ready
  ]
  deletion_protection = false

  template {
    service_account = google_service_account.cloud_run_sa.email

    vpc_access {
      connector = google_vpc_access_connector.connector.id
      egress    = "ALL_TRAFFIC"
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.gcp_project_id}/${local.artifact_registry_name}/dashboard:latest"

      resources {
        limits = local.resource_limits
      }

      ports {
        name           = "http1"
        container_port = 8080
      }

      # Common database environment variables
      dynamic "env" {
        for_each = local.db_env_vars
        content {
          name  = env.key
          value = env.value
        }
      }

      # Common Slack environment variables
      dynamic "env" {
        for_each = local.slack_env_vars
        content {
          name  = env.key
          value = env.value
        }
      }

      # Secret-based environment variables
      dynamic "env" {
        for_each = local.secret_env_vars
        content {
          name = env.key
          value_source {
            secret_key_ref {
              secret  = env.value.secret
              version = env.value.version
            }
          }
        }
      }

      # Dashboard-specific environment variables
      env {
        name  = "_TENANT"
        value = var.tenant
      }

      env {
        name  = "POSTGRES_SCHEMA"
        value = "public"
      }

      env {
        name = "_TRIGGER_REBUILD"
        value = md5(join("", [
          for f in fileset("${path.module}/../../dashboard", "**/*") : filemd5("${path.module}/../../dashboard/${f}")
        ]))
      }
    }
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
}

# Local values for IAM bindings
locals {
  # Jobs that need invoker permissions
  job_invoker_bindings = {
    collector = {
      location = google_cloud_run_v2_job.collector.location
      name     = google_cloud_run_v2_job.collector.name
    }
    datapipeline = {
      location = google_cloud_run_v2_job.datapipeline.location
      name     = google_cloud_run_v2_job.datapipeline.name
    }
  }
}

# Consolidated IAM binding for running jobs using for_each
resource "google_cloud_run_v2_job_iam_binding" "job_invokers" {
  for_each = local.job_invoker_bindings

  project  = var.gcp_project_id
  location = each.value.location
  name     = each.value.name
  role     = "roles/run.invoker"
  members = [
    "serviceAccount:${google_service_account.cloud_run_sa.email}"
  ]
  depends_on = [time_sleep.all_apis_ready]
}

# IAM binding for dashboard service (public access)
resource "google_cloud_run_v2_service_iam_binding" "dashboard_invoker" {
  project    = var.gcp_project_id
  location   = google_cloud_run_v2_service.dashboard.location
  name       = google_cloud_run_v2_service.dashboard.name
  role       = "roles/run.invoker"
  members    = ["allUsers"] # Public access for web dashboard
  depends_on = [time_sleep.all_apis_ready]
}
