# Get current Azure client configuration
data "azurerm_client_config" "current" {}

# Create Key Vault with RBAC authorization
resource "azurerm_key_vault" "kv" {
  name                      = "ccm-${var.tenant}-keyvault"
  location                  = azurerm_resource_group.rg.location
  resource_group_name       = azurerm_resource_group.rg.name
  tenant_id                 = data.azurerm_client_config.current.tenant_id
  sku_name                  = "standard"
  enable_rbac_authorization = true
  purge_protection_enabled  = false

  tags = var.tags

}

# Add RBAC role assignment for current user
resource "azurerm_role_assignment" "kv_current_user" {
  for_each = toset([
    "Key Vault Administrator",
    "Key Vault Secrets Officer",
    "Key Vault Secrets User"
  ])

  scope                = azurerm_key_vault.kv.id
  role_definition_name = each.value
  principal_id         = data.azurerm_client_config.current.object_id

  timeouts {
    create = "5m"
  }
}

resource "time_sleep" "wait_for_rbac" {
  depends_on      = [azurerm_role_assignment.kv_current_user]
  create_duration = "300s"
}

# Configure diagnostic settings
resource "azurerm_monitor_diagnostic_setting" "kv" {
  name                       = "ccm-${var.tenant}-diagnostics"
  target_resource_id         = azurerm_key_vault.kv.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id

  enabled_log {
    category = "AuditEvent"
  }
}

# Create secrets in Key Vault
resource "azurerm_key_vault_secret" "secrets" {
  for_each = var.secrets

  name         = lower(replace(each.key, "_", "-")) # azure-legal name
  value        = each.value
  key_vault_id = azurerm_key_vault.kv.id
  depends_on = [
    azurerm_key_vault.kv,
    azurerm_key_vault_access_policy.user,
    time_sleep.wait_for_rbac
  ]
}

resource "azurerm_key_vault_access_policy" "user" {
  key_vault_id = azurerm_key_vault.kv.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = data.azurerm_client_config.current.object_id

  secret_permissions = [
    "Get",
    "List",
    "Set",
    "Delete",
    "Purge",
    "Recover"
  ]

  certificate_permissions = [
    "Get",
    "List",
    "Create",
    "Delete",
    "Update"
  ]
  depends_on = [
    azurerm_key_vault.kv,
    time_sleep.wait_for_rbac
  ]
}
