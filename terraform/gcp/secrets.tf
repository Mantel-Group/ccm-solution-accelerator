# Database password secret
resource "google_secret_manager_secret" "db_password" {
  secret_id = "ccm-${var.tenant}-db-password"

  replication {
    auto {}
  }

  labels     = var.tags
  depends_on = [time_sleep.all_apis_ready]
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_master.result

  depends_on = [
    google_project_service.secretmanager,
    time_sleep.all_apis_ready
  ]
}

# Database connection string secret
resource "google_secret_manager_secret" "db_connection" {
  secret_id = "ccm-${var.tenant}-db-connection"

  replication {
    auto {}
  }

  labels = var.tags
  depends_on = [
    google_project_service.secretmanager,
    time_sleep.all_apis_ready
  ]
}

resource "google_secret_manager_secret_version" "db_connection" {
  secret      = google_secret_manager_secret.db_connection.id
  secret_data = "postgresql://${google_sql_user.database_user.name}:${urlencode(random_password.db_master.result)}@${google_sql_database_instance.database.private_ip_address}:5432/${google_sql_database.database.name}"

  depends_on = [
    google_sql_database_instance.database,
    google_sql_database.database,
    google_sql_user.database_user,
    google_secret_manager_secret_version.db_password,
    google_service_networking_connection.private_vpc_connection,
    google_project_service.secretmanager,
    time_sleep.all_apis_ready
  ]
}

# Dynamic API Secrets - creates secrets for all items in var.secrets
resource "google_secret_manager_secret" "api_secrets" {
  for_each = var.secrets

  secret_id = "ccm-${var.tenant}-${lower(replace(each.key, "_", "-"))}"

  replication {
    auto {}
  }

  labels = var.tags

  depends_on = [
    google_project_service.secretmanager,
    time_sleep.all_apis_ready
  ]
}

resource "google_secret_manager_secret_version" "api_secrets" {
  for_each = var.secrets

  secret      = google_secret_manager_secret.api_secrets[each.key].id
  secret_data = each.value

  depends_on = [
    google_project_service.secretmanager,
    time_sleep.all_apis_ready
  ]
}
