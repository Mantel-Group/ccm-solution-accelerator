resource "aws_cloudwatch_log_group" "log_group" {
  name              = "/ecs/ccm-${var.tenant}-log-group"
  retention_in_days = 7
  tags              = var.tags
}