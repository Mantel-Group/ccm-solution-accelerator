locals {
  container_cpu_vcpu  = var.container_cpu / 1024
  container_memory_gb = format("%.0fGi", var.container_memory / 1024)

  # Function to offset cron schedule by 2 hours
  datapipeline_cron_schedule = replace(
    var.cron_schedule,
    "/^(\\S+)\\s+(\\S+)\\s+(\\S+)\\s+(\\S+)\\s+(\\S+)$/",
    "$1 ${split(" ", var.cron_schedule)[1] == "*" ? "2" : format("%d", (tonumber(split(" ", var.cron_schedule)[1]) + 2) % 24)} $3 $4 $5"
  )
}

# Create Log Analytics workspace for Container Apps
resource "azurerm_log_analytics_workspace" "law" {
  name                = "ccm-${var.tenant}-log-analytics-workspace"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = var.tags
}

# Create Container Apps Environment
resource "azurerm_container_app_environment" "cae" {
  name                               = "ccm-${var.tenant}-container-app-environment"
  location                           = azurerm_resource_group.rg.location
  resource_group_name                = azurerm_resource_group.rg.name
  log_analytics_workspace_id         = azurerm_log_analytics_workspace.law.id
  infrastructure_subnet_id           = azurerm_subnet.container_apps.id
  infrastructure_resource_group_name = "ME_cae-${var.tenant}_rg-continuous-assurance-${var.tenant}_${var.region}"

  workload_profile {
    name                  = "Consumption"
    workload_profile_type = "Consumption"
    minimum_count         = null
    maximum_count         = null
  }

  tags = var.tags
}

# Datapipeline Container App
resource "azurerm_container_app_job" "datapipeline_job" {
  name                         = "ccm-${var.tenant}-datapipeline-job"
  container_app_environment_id = azurerm_container_app_environment.cae.id
  resource_group_name          = azurerm_resource_group.rg.name
  location                     = azurerm_resource_group.rg.location
  tags                         = var.tags
  workload_profile_name        = "Consumption"

  identity {
    type = "SystemAssigned"
  }

  # Schedule trigger set 2 hours after collector job
  schedule_trigger_config {
    cron_expression = local.datapipeline_cron_schedule
  }

  secret {
    name  = "db-password"
    value = azurerm_postgresql_flexible_server.db.administrator_password
  }

  secret {
    name  = "registry-password"
    value = azurerm_container_registry.acr.admin_password
  }

  template {
    container {
      name   = "datapipeline"
      image  = "${azurerm_container_registry.acr.login_server}/datapipeline:latest"
      cpu    = local.container_cpu_vcpu
      memory = local.container_memory_gb

      env {
        name  = "_TENANT"
        value = var.tenant
      }
      env {
        name  = "ALERT_SLACK_WEBHOOK"
        value = var.alert_slack_webhook
      }
      env {
        name  = "ALERT_SLACK_TOKEN"
        value = var.alert_slack_token
      }
      env {
        name  = "ALERT_SLACK_CHANNEL"
        value = var.alert_slack_channel
      }
      env {
        name  = "POSTGRES_ENDPOINT"
        value = azurerm_postgresql_flexible_server.db.fqdn
      }
      env {
        name  = "POSTGRES_DATABASE"
        value = azurerm_postgresql_flexible_server_database.db.name
      }
      env {
        name  = "POSTGRES_USERNAME"
        value = azurerm_postgresql_flexible_server.db.administrator_login
      }
      env {
        name        = "POSTGRES_PASSWORD"
        secret_name = "db-password"
      }
      env {
        name  = "POSTGRES_SCHEMA"
        value = "public"
      }
      env {
        name  = "POSTGRES_PORT"
        value = "5432"
      }

      env {
        name = "_TRIGGER_REBUILD"
        value = md5(join("", [
          for f in fileset("${path.module}/../../datapipeline", "**/*") : filemd5("${path.module}/../../datapipeline/${f}")
        ]))
      }
    }
  }

  replica_timeout_in_seconds = 300
  replica_retry_limit        = 1

  registry {
    server               = azurerm_container_registry.acr.login_server
    username             = azurerm_container_registry.acr.admin_username
    password_secret_name = "registry-password"
  }

  depends_on = [
    azurerm_key_vault_secret.secrets,
    azurerm_container_registry.acr,
    null_resource.build_collector,
    azurerm_postgresql_flexible_server.db,
    azurerm_key_vault.kv
  ]
}

# Collector Container App
resource "azurerm_container_app_job" "collector_job" {
  name                         = "ccm-${var.tenant}-collector-job"
  container_app_environment_id = azurerm_container_app_environment.cae.id
  resource_group_name          = azurerm_resource_group.rg.name
  location                     = azurerm_resource_group.rg.location
  tags                         = var.tags
  workload_profile_name        = "Consumption"

  identity {
    type = "SystemAssigned"
  }

  schedule_trigger_config {
    cron_expression = var.cron_schedule
  }

  dynamic "secret" {
    for_each = var.secrets
    content {
      name  = lower(replace(secret.key, "_", "-"))
      value = secret.value
    }
  }

  secret {
    name  = "db-password"
    value = azurerm_postgresql_flexible_server.db.administrator_password
  }

  secret {
    name  = "registry-password"
    value = azurerm_container_registry.acr.admin_password
  }

  template {
    container {
      name   = "collector"
      image  = "${azurerm_container_registry.acr.login_server}/collector:latest"
      cpu    = local.container_cpu_vcpu
      memory = local.container_memory_gb

      env {
        name  = "_TENANT"
        value = var.tenant
      }
      env {
        name  = "ALERT_SLACK_WEBHOOK"
        value = var.alert_slack_webhook
      }
      env {
        name  = "ALERT_SLACK_TOKEN"
        value = var.alert_slack_token
      }
      env {
        name  = "ALERT_SLACK_CHANNEL"
        value = var.alert_slack_channel
      }
      env {
        name  = "POSTGRES_ENDPOINT"
        value = azurerm_postgresql_flexible_server.db.fqdn
      }
      env {
        name  = "POSTGRES_DATABASE"
        value = azurerm_postgresql_flexible_server_database.db.name
      }
      env {
        name  = "POSTGRES_USERNAME"
        value = azurerm_postgresql_flexible_server.db.administrator_login
      }
      env {
        name        = "POSTGRES_PASSWORD"
        secret_name = "db-password"
      }
      env {
        name  = "POSTGRES_SCHEMA"
        value = "source"
      }
      env {
        name  = "POSTGRES_PORT"
        value = "5432"
      }

      env {
        name = "_TRIGGER_REBUILD"
        value = md5(join("", concat([
          for f in fileset("${path.module}/../../collector", "**/*") : filemd5("${path.module}/../../collector/${f}")
        ], [md5("${var.dashboard_username}:${var.dashboard_password}")])))
      }

      dynamic "env" {
        for_each = var.secrets
        content {
          name        = env.key
          secret_name = lower(replace(env.key, "_", "-"))
        }
      }
    }
  }

  replica_timeout_in_seconds = 86400
  replica_retry_limit        = 1

  registry {
    server               = azurerm_container_registry.acr.login_server
    username             = azurerm_container_registry.acr.admin_username
    password_secret_name = "registry-password"
  }

  depends_on = [
    azurerm_key_vault_secret.secrets,
    azurerm_container_registry.acr,
    null_resource.build_collector,
    azurerm_postgresql_flexible_server.db,
    azurerm_key_vault.kv
  ]
}

# Dashboard Container App
resource "azurerm_container_app" "dashboard" {
  name                         = "ccm-${var.tenant}-dashboard"
  container_app_environment_id = azurerm_container_app_environment.cae.id
  resource_group_name          = azurerm_resource_group.rg.name
  revision_mode                = "Single"

  template {
    min_replicas = 0
    max_replicas = 1
    container {
      name   = "dashboard"
      image  = "${azurerm_container_registry.acr.login_server}/dashboard:latest"
      cpu    = local.container_cpu_vcpu
      memory = local.container_memory_gb

      env {
        name  = "_TENANT"
        value = var.tenant
      }
      env {
        name  = "ALERT_SLACK_WEBHOOK"
        value = var.alert_slack_webhook
      }
      env {
        name  = "ALERT_SLACK_TOKEN"
        value = var.alert_slack_token
      }
      env {
        name  = "ALERT_SLACK_CHANNEL"
        value = var.alert_slack_channel
      }
      env {
        name  = "POSTGRES_ENDPOINT"
        value = azurerm_postgresql_flexible_server.db.fqdn
      }
      env {
        name  = "POSTGRES_DATABASE"
        value = azurerm_postgresql_flexible_server_database.db.name
      }
      env {
        name  = "POSTGRES_USERNAME"
        value = azurerm_postgresql_flexible_server.db.administrator_login
      }
      env {
        name        = "POSTGRES_PASSWORD"
        secret_name = "db-password"
      }
      env {
        name  = "POSTGRES_SCHEMA"
        value = "public"
      }
      env {
        name  = "POSTGRES_PORT"
        value = "5432"
      }
      env {
        name = "_TRIGGER_REBUILD"
        value = md5(join("", [
          for f in fileset("${path.module}/../../dashboard", "**/*") : filemd5("${path.module}/../../dashboard/${f}")
        ]))
      }
    }
  }

  secret {
    name  = "db-password"
    value = azurerm_postgresql_flexible_server.db.administrator_password
  }

  secret {
    name  = "registry-password"
    value = azurerm_container_registry.acr.admin_password
  }

  registry {
    server               = azurerm_container_registry.acr.login_server
    username             = azurerm_container_registry.acr.admin_username
    password_secret_name = "registry-password"
  }

  ingress {
    external_enabled = true
    target_port      = 8080
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  tags                  = var.tags
  workload_profile_name = "Consumption"

  depends_on = [
    azurerm_container_registry.acr,
    null_resource.build_dashboard,
    azurerm_postgresql_flexible_server.db,
    azurerm_key_vault.kv,
    azurerm_key_vault_secret.secrets
  ]
}

