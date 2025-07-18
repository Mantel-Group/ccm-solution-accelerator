# Create Azure Container Registry
resource "azurerm_container_registry" "acr" {
  name                = "ccm${var.tenant}acr"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = true

  tags = var.tags
}

# Store ACR admin credentials in Key Vault
resource "azurerm_key_vault_secret" "acr_admin_username" {
  name         = "acr-admin-username"
  value        = azurerm_container_registry.acr.admin_username
  key_vault_id = azurerm_key_vault.kv.id

  depends_on = [
    azurerm_key_vault.kv,
    azurerm_key_vault_access_policy.user,
    time_sleep.wait_for_rbac
  ]
}

resource "azurerm_key_vault_secret" "acr_admin_password" {
  name         = "acr-admin-password"
  value        = azurerm_container_registry.acr.admin_password
  key_vault_id = azurerm_key_vault.kv.id

  depends_on = [
    azurerm_key_vault.kv,
    azurerm_key_vault_access_policy.user,
    time_sleep.wait_for_rbac
  ]
}