# variables.tf
variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "disaster-recovery-rg"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "eastus"  # Changed from centralindia
}

variable "storage_account_name" {
  description = "Name of the storage account (must be globally unique)"
  type        = string
  default     = "drbackup2025"
}

variable "app_service_plan_name" {
  description = "Name of the App Service Plan"
  type        = string
  default     = "disaster-recovery-plan"
}

variable "web_app_name" {
  description = "Name of the web app (must be globally unique)"
  type        = string
  default     = "disaster-recovery-dashboard-joshua"
}

variable "github_repo_url" {
  description = "GitHub repository URL"
  type        = string
  default     = "https://github.com/joshua-yowin/disaster-recovery-system"
}
