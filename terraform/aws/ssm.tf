resource "aws_ssm_parameter" "db_secret" {
  name        = "/ContinuousControlsMonitoring/${var.tenant}/database_password"
  description = "This is the master password to the contiuous assurance Databse"
  type        = "SecureString"
  value       = random_password.db_master.result
}

resource "aws_ssm_parameter" "secrets" {
  for_each = var.secrets

  name  = "/ContinuousControlsMonitoring/${var.tenant}/${each.key}"
  type  = "SecureString"
  value = each.value
  lifecycle {
    ignore_changes = [value]
  }
  tier = "Standard"

  tags = var.tags
}

resource "random_password" "db_master" {
  length  = 20
  special = false
}
