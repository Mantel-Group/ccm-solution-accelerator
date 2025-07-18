output "datapipeline_job_trigger_command" {
  description = "AWS CLI command to manually trigger the datapipeline job"
  value       = "aws ecs run-task --cluster ${aws_ecs_cluster.main.name} --launch-type FARGATE --task-definition ${aws_ecs_task_definition.datapipeline.family} --network-configuration \"awsvpcConfiguration={subnets=${jsonencode(var.aws_container_subnets)},securityGroups=[${aws_security_group.ecs_tasks.id}],assignPublicIp=ENABLED}\" --platform-version LATEST"
}

output "collector_job_trigger_command" {
  description = "AWS CLI command to manually trigger the collector job"
  value       = "aws ecs run-task --cluster ${aws_ecs_cluster.main.name} --launch-type FARGATE --task-definition ${aws_ecs_task_definition.collector.family} --network-configuration \"awsvpcConfiguration={subnets=${jsonencode(var.aws_container_subnets)},securityGroups=[${aws_security_group.ecs_tasks.id}],assignPublicIp=ENABLED}\" --platform-version LATEST"
}

output "dashboard_url" {
  description = "Dashboard URL"
  value       = aws_lambda_function_url.dashboard_redirect.function_url
}

output "database" {
  description = "The Postgres Database name"
  value       = aws_db_instance.database.db_name
}

output "database_username" {
  description = "The Database username"
  value       = var.db_username
}

output "database_server_fqdn" {
  description = "The FQDN of the PostgreSQL Server"
  value       = aws_db_instance.database.endpoint
}
