# ========= General configuration

variable "tenant" {
  type        = string
  description = "The tenant to which this deployment corresponds to"
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
  description = "The region where the solution will be deployed to"
  default     = "australia-southeast1"
}

variable "gcp_project_id" {
  type        = string
  description = "GCP Project ID"
}


variable "tags" {
  description = "Default tags to apply to all resources"
  type        = map(string)
  default = {
    Project = "Continuous Controls Monitoring Starter Template"
  }
}

# ========= Network configuration

variable "gcp_vpc_cidr" {
  type        = string
  description = "CIDR block for VPC"
  default     = "10.0.0.0/16"
}

variable "gcp_database_subnet_cidr" {
  type        = string
  description = "CIDR block for database subnet"
  default     = "10.0.1.0/24"
}

variable "gcp_container_subnet_cidr" {
  type        = string
  description = "CIDR block for container subnet"
  default     = "10.0.2.0/24"
}

# ========= Database specific variables

variable "db_name" {
  type        = string
  description = "Name of the database to create"
  default     = "continuous_assurance"
}

variable "db_username" {
  type        = string
  description = "The database username to define"
  default     = "ContinuousAssurance"
}

variable "db_instance_size" {
  type        = string
  description = "Cloud specific database instance size to use"
  default     = "db-f1-micro"
}

variable "db_storage" {
  type        = string
  description = "Database Storage in GB"
  default     = 20
}

variable "db_public_facing" {
  type        = bool
  description = "Whether the database should be publicly accessible"
  default     = false
}

variable "db_cidr_inbound_allow" {
  type        = list(string)
  description = "List of CIDR blocks allowed to access the database if public"
  default     = []
}

variable "db_version" {
  type        = string
  description = "PostgreSQL version"
  default     = "POSTGRES_14"
}

# ==== Container stuff

variable "cron_schedule" {
  type        = string
  description = "The cron schedule when the collector job is expected to kick off"
  default     = "15 21 * * *"
}

variable "container_cpu" {
  description = "CPU limit for containers"
  type        = string
  default     = "1.0"
}

variable "container_memory" {
  type        = string
  description = "Container instance memory to provision (in MiB)"
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

# ===== General 

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
    DOMAINS             = "CHANGE ME"
  }
}
