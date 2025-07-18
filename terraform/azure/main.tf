terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.31.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.azure_subscription_id

}

resource "azurerm_resource_group" "rg" {
  name     = var.azure_resource_group_name
  location = var.region
  tags     = var.tags
}
