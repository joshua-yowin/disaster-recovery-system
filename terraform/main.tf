# main.tf
terraform {
  required_version = ">= 1.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

# Resource Group - In eastus (actual location)
resource "azurerm_resource_group" "disaster_recovery" {
  name     = var.resource_group_name
  location = "eastus"  # Actual location

  tags = {
    Environment = "Production"
    Project     = "Disaster Recovery System"
    ManagedBy   = "Terraform"
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [location]  # Don't try to change location
  }
}

# Storage Account - In centralindia (actual location)
resource "azurerm_storage_account" "backup_storage" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.disaster_recovery.name
  location                 = "centralindia"  # Actual location (different from RG!)

  account_tier             = "Standard"
  account_replication_type = "LRS"

  # Match actual Azure settings
  allow_nested_items_to_be_public  = false
  cross_tenant_replication_enabled = false
  min_tls_version                  = "TLS1_0"

  tags = {
    Environment = "Production"
    Purpose     = "Backup Storage"
  }

  lifecycle {
    ignore_changes = [location]  # Don't try to change location
  }
}

# Storage Container for Backups
resource "azurerm_storage_container" "backups" {
  name                  = "backups"
  storage_account_name  = azurerm_storage_account.backup_storage.name
  container_access_type = "private"
}

# App Service Plan - In centralindia (actual location)
resource "azurerm_service_plan" "app_service_plan" {
  name                = var.app_service_plan_name
  resource_group_name = azurerm_resource_group.disaster_recovery.name
  location            = "centralindia"  # Actual location
  os_type             = "Linux"
  sku_name            = "F1"

  tags = {
    Environment = "Production"
  }

  lifecycle {
    ignore_changes = [location]  # Don't try to change location
  }
}

# Linux Web App - In centralindia (follows App Service Plan)
resource "azurerm_linux_web_app" "disaster_recovery_app" {
  name                = var.web_app_name
  resource_group_name = azurerm_resource_group.disaster_recovery.name
  location            = "centralindia"  # Actual location
  service_plan_id     = azurerm_service_plan.app_service_plan.id

  # Match actual Azure settings
  client_affinity_enabled                        = true
  ftp_publish_basic_authentication_enabled       = false
  webdeploy_publish_basic_authentication_enabled = false
  https_only                                     = false

  site_config {
    always_on = false

    ftps_state    = "FtpsOnly"
    http2_enabled = true

    application_stack {
      python_version = "3.11"
    }

    app_command_line = "gunicorn --bind=0.0.0.0:8000 --timeout 600 app:app"
  }

  app_settings = {
    "AZURE_STORAGE_CONNECTION_STRING" = azurerm_storage_account.backup_storage.primary_connection_string
    "AZURE_CONTAINER_NAME"            = azurerm_storage_container.backups.name
    "WEBSITES_PORT"                   = "8000"
    "SCM_DO_BUILD_DURING_DEPLOYMENT"  = "1"
    "FLASK_DEBUG"                     = "False"
    "DASHBOARD_PORT"                  = "8000"
  }

  tags = {
    Environment = "Production"
    Application = "Disaster Recovery Dashboard"
  }
}
