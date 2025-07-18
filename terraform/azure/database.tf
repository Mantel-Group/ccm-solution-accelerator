# Generate random password for database
resource "random_password" "db_password" {
  length  = 20
  special = true
}

# Create PostgreSQL Flexible Server
resource "azurerm_postgresql_flexible_server" "db" {
  name                   = "ccm-${var.tenant}-postgres"
  resource_group_name    = azurerm_resource_group.rg.name
  location               = azurerm_resource_group.rg.location
  version                = var.db_version
  tags                   = var.tags
  administrator_login    = var.db_username
  administrator_password = random_password.db_password.result

  # Fix database configuration
  sku_name   = var.db_instance_size
  storage_mb = var.db_storage * 1024

  # Add proper network configuration
  delegated_subnet_id           = azurerm_subnet.database.id
  private_dns_zone_id           = azurerm_private_dns_zone.database.id
  public_network_access_enabled = var.db_public_facing

  # Backup configuration
  backup_retention_days        = 7
  geo_redundant_backup_enabled = false

  lifecycle {
    prevent_destroy = false
    ignore_changes  = [zone]
  }

  depends_on = [
    azurerm_private_dns_zone_virtual_network_link.database
  ]
}

resource "azurerm_postgresql_flexible_server_database" "db" {
  name      = var.db_name
  server_id = azurerm_postgresql_flexible_server.db.id
}

# Set PostgreSQL server configuration for max_connections
resource "azurerm_postgresql_flexible_server_configuration" "max_connections" {
  name      = "max_connections"
  server_id = azurerm_postgresql_flexible_server.db.id
  value     = "100"

}

# Store the database password in Key Vault
resource "azurerm_key_vault_secret" "db_password" {
  name         = "database-password"
  value        = random_password.db_password.result
  key_vault_id = azurerm_key_vault.kv.id
  tags         = var.tags

  depends_on = [
    azurerm_key_vault.kv,
    azurerm_key_vault_access_policy.user,
    time_sleep.wait_for_rbac
  ]
}

# Allow access from Azure services
resource "azurerm_postgresql_flexible_server_firewall_rule" "azure_services" {
  name             = "allow-azure-services"
  server_id        = azurerm_postgresql_flexible_server.db.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

resource "azurerm_private_dns_zone" "database" {
  name                = "${var.tenant}.postgres.database.azure.com"
  resource_group_name = azurerm_resource_group.rg.name
  tags                = var.tags
}

resource "azurerm_private_dns_zone_virtual_network_link" "database" {
  name                  = "postgres-dns-link"
  private_dns_zone_name = azurerm_private_dns_zone.database.name
  resource_group_name   = azurerm_resource_group.rg.name
  virtual_network_id    = azurerm_virtual_network.vnet.id
  registration_enabled  = false
  tags                  = var.tags
}

