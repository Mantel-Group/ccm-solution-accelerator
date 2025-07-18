resource "aws_scheduler_schedule_group" "deploy_collector" {
  name = "ccm-${var.tenant}-schedule-group"
  tags = var.tags
}

resource "aws_cloudwatch_event_rule" "collector_completion_trigger" {
  name        = "ccm-${var.tenant}-collector-completion-trigger"
  description = "Trigger datapipeline when collector task completes successfully"

  event_pattern = jsonencode({
    source      = ["aws.ecs"]
    detail-type = ["ECS Task State Change"]
    detail = {
      clusterArn        = [aws_ecs_cluster.main.arn]
      taskDefinitionArn = [aws_ecs_task_definition.collector.arn]
      lastStatus        = ["STOPPED"]
    }
  })
  tags = var.tags
}

resource "aws_cloudwatch_event_target" "trigger_datapipeline" {
  rule     = aws_cloudwatch_event_rule.collector_completion_trigger.name
  arn      = aws_ecs_cluster.main.arn
  role_arn = aws_iam_role.scheduler.arn

  ecs_target {
    task_definition_arn = trimsuffix(aws_ecs_task_definition.datapipeline.arn, ":${aws_ecs_task_definition.datapipeline.revision}")

    launch_type = "FARGATE"

    network_configuration {
      assign_public_ip = true
      security_groups  = [aws_security_group.ecs_tasks.id]
      subnets          = var.aws_container_subnets
    }
  }
}

resource "aws_scheduler_schedule" "deploy_collector" {
  name                = "ccm-${var.tenant}-schedule-collector"
  group_name          = aws_scheduler_schedule_group.deploy_collector.name
  schedule_expression = "cron(${var.cron_schedule})"
  state               = "ENABLED"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = aws_ecs_cluster.main.arn
    role_arn = aws_iam_role.scheduler.arn

    ecs_parameters {
      task_definition_arn = trimsuffix(aws_ecs_task_definition.collector.arn, ":${aws_ecs_task_definition.collector.revision}")
      launch_type         = "FARGATE"

      network_configuration {
        assign_public_ip = true
        security_groups  = [aws_security_group.ecs_tasks.id]
        subnets          = var.aws_container_subnets
      }
    }
  }
}
