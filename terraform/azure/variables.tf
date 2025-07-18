# ========= General configuration

variable "tenant" {
  type        = string
  description = "Environment name/tenant identifier"
  default     = "default"
}

variable "alert_slack_webhook" {
  type        = string
  description = "When using Slack in a Webhook mode, specify the webhook here"
  default     = ""
}

variable "alert_slack_token" {
  type    = string
  default = "Provide a slack token if you use it in token mode"
}

variable "alert_slack_channel" {
  type    = string
  default = "Provide the slack channel name where alerts are to be sent to (require the slack token)"
}

# ========= Cloud specific

variable "region" {
  type        = string
  description = "Azure region to deploy resources"
  default     = "australiaeast"
}

variable "azure_subscription_id" {
  type        = string
  description = "Azure subscription id"
}

variable "azure_resource_group_name" {
  type        = string
  description = "Name of the resource group to use"
}

variable "tags" {
  description = "Default tags to apply to all resources"
  type        = map(string)
  default = {
    Project = "Continuous Controls Monitoring Starter Template"
  }
}

# ========= Network configuration

variable "azure_vnet_cidr" {
  type        = list(string)
  description = "Address space for Virtual Network"
  default     = ["10.0.0.0/16"]
}

variable "azure_subnet_container_cidr" {
  type        = list(string)
  description = "Address prefix for Container Apps subnet"
  default     = ["10.0.0.0/21"]
}

variable "azure_subnet_database_cidr" {
  type        = list(string)
  description = "Address prefix for Database subnet"
  default     = ["10.0.8.0/24"]
}
# ========= Database specific variables

variable "db_name" {
  type        = string
  description = "Name of the database to create"
  default     = "continuous_assurance"
}

variable "db_version" { 
  type        = string
  description = "The Postgres database version to use"
  default     = "16"
}

variable "db_username" {
  type        = string
  description = "The database username to define"
  default     = "ContinuousAssurance"
}

variable "db_instance_size" {
  type        = string
  description = "database_sku_name"
  default     = "B_Standard_B1ms"
}

variable "db_storage" {
  type        = string
  description = "Database storage in GB"
  default     = 32
}

variable "db_public_facing" {
  type        = bool
  description = "Whether the database should be public facing"
  default     = false
}

variable "db_cidr_inbound_allow" {
  type        = list(string)
  description = "List of CIDR blocks allowed to access the database if public"
  default     = []
}

# ======= Containers

variable "cron_schedule" {
  type        = string
  description = "The cron schedule when the collector job is expected to kick off"
  default     = "0 18 * * *"
}

variable "container_cpu" {
  type        = string
  description = "Fargate instance CPU units to provision (1 vCPU = 1024 CPU units)"
  default     = "1024"
}

variable "container_memory" {
  type        = string
  description = "Fargate instance memory to provision (in MiB)"
  default     = "2048"
}

# ===== Dashboard

variable "dashboard_cidr_inbound_allow" {
  type        = list(string)
  description = "The CIDR range that is allowed to connect to the dashboard"
  default     = ["0.0.0.0/0"]
}

variable "dashboard_username" {
  type        = string
  description = "Admin username to use on the dashboard"
  default     = "admin"
}

variable "dashboard_password" {
  type        = string
  description = "Admin password to use on the dashboard"
  default     = "s3cretW0rd"
}

# ====== Secret stuff

variable "secrets" {
  description = "Map of secret variables used by API calls"
  type        = map(string)
  default = {
    FALCON_CLIENT_ID    = "CHANGE ME"
    FALCON_SECRET       = "CHANGE ME"
    TENABLE_ACCESS_KEY  = "CHANGE ME"
    TENABLE_SECRET_KEY  = "CHANGE ME"
    KNOWBE4_TOKEN       = "CHANGE ME"
    OKTA_TOKEN          = "CHANGE ME"
    OKTA_DOMAIN         = "CHANGE ME"
    AZURE_TENANT_ID     = "CHANGE ME"
    AZURE_CLIENT_ID     = "CHANGE ME"
    AZURE_CLIENT_SECRET = "CHANGE ME"
    DOMAINS             = "mantelgroup.com.au,mantelgroup.co.nz,mantelgroup.co.vn"
  }
}