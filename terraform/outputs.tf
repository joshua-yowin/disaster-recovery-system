# outputs.tf
output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.disaster_recovery.name
}

output "storage_account_name" {
  description = "Name of the storage account"
  value       = azurerm_storage_account.backup_storage.name
}

output "storage_connection_string" {
  description = "Storage account connection string"
  value       = azurerm_storage_account.backup_storage.primary_connection_string
  sensitive   = true
}

output "web_app_url" {
  description = "URL of the deployed web app"
  value       = "https://${azurerm_linux_web_app.disaster_recovery_app.default_hostname}"
}

output "web_app_name" {
  description = "Name of the web app"
  value       = azurerm_linux_web_app.disaster_recovery_app.name
}
