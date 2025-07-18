# Random password for database
resource "random_password" "db_master" {
  length  = 20
  special = false
}

# Cloud SQL PostgreSQL instance
resource "google_sql_database_instance" "database" {
  name                = "ccm-${var.tenant}-db"
  database_version    = var.db_version
  region              = var.region
  deletion_protection = false

  depends_on = [google_service_networking_connection.private_vpc_connection, time_sleep.all_apis_ready]

  settings {
    tier      = var.db_instance_size
    disk_size = var.db_storage

    ip_configuration {
      ipv4_enabled    = false                         # No public IP
      private_network = google_compute_network.vpc.id # Use private network
    }

    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
      backup_retention_settings {
        retained_backups = 7
      }
      transaction_log_retention_days = 7
    }

    database_flags {
      name  = "log_statement"
      value = "all"
    }

    database_flags {
      name  = "max_connections"
      value = "300"
    }
  }
}

# Database within the instance
resource "google_sql_database" "database" {
  name     = "CCM${var.tenant}"
  instance = google_sql_database_instance.database.name
}

# Database user
resource "google_sql_user" "database_user" {
  name     = "ContinuousAssurance"
  instance = google_sql_database_instance.database.name
  password = random_password.db_master.result
}
