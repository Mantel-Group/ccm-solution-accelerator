output "dashboard_url" {
  value = "https://${azurerm_container_app.dashboard.ingress[0].fqdn}"
}

output "database" {
  value       = azurerm_postgresql_flexible_server.db.name
  description = "Postgres database name"
}

output "database_username" {
  value       = azurerm_postgresql_flexible_server.db.administrator_login
  description = "Postgres username"
}

output "database_server_fqdn" {
  value       = azurerm_postgresql_flexible_server.db.fqdn
  description = "Postgres FQDN"
}

output "collector_job_trigger_command" {
  description = "Azure CLI command to manually trigger the collector job"
  value       = "az containerapp job start --name ccm-${var.tenant}-collector-job --resource-group ${azurerm_resource_group.rg.name}"
}

output "datapipeline_job_trigger_command" {
  description = "Azure CLI command to manually trigger the datapipeline job"
  value       = "az containerapp job start --name ccm-${var.tenant}-datapipeline-job --resource-group ${azurerm_resource_group.rg.name}"
}