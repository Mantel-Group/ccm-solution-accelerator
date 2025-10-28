resource "aws_ecs_cluster" "main" {
  name = "ccm-${var.tenant}-cluster"

  tags = var.tags
}

resource "aws_ecs_task_definition" "collector" {
  family                   = "ccm-${var.tenant}-family-collector"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.container_cpu
  memory                   = var.container_memory
  container_definitions = jsonencode([
    {
      name  = "ccm-${var.tenant}-task-collector"
      image = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.region}.amazonaws.com/collector-${var.tenant}:latest"
      essential = true
      cpu = 0
      mountPoints      = []
      systemControls   = []
      volumesFrom      = []
      secrets = concat(
        [
          for name, _ in aws_ssm_parameter.secrets : {
            name      = name
            valueFrom = aws_ssm_parameter.secrets[name].arn
          }
        ],
        [
          {
            name      = "POSTGRES_PASSWORD"
            valueFrom = aws_ssm_parameter.db_secret.arn
          }
        ]
      )
      environment = [
        {
          name  = "ALERT_SLACK_WEBHOOK"
          value = var.alert_slack_webhook
        },
        {
          name  = "ALERT_SLACK_TOKEN"
          value = var.alert_slack_token
        },
        {
          name  = "ALERT_SLACK_CHANNEL"
          value = var.alert_slack_channel
        },
        {
          name  = "POSTGRES_ENDPOINT"
          value = aws_db_instance.database.address
        },
        {
          name  = "POSTGRES_USERNAME"
          value = var.db_username
        },
        {
          name  = "POSTGRES_SCHEMA"
          value = "source"
        },
        {
          name  = "POSTGRES_DATABASE"
          value = aws_db_instance.database.db_name
        },
        {
          name  = "POSTGRES_PORT"
          value = tostring(aws_db_instance.database.port)
        },
        {
          name  = "_TENANT"
          value = var.tenant
        },
        {
          name = "_TRIGGER_REBUILD"
          value = md5(join("", 
            [for f in fileset("${path.module}/../../collector", "**/*") : filemd5("${path.module}/../../collector/${f}")],
          ))
        }
      ],
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.log_group.name
          "awslogs-stream-prefix" = var.tenant
          "awslogs-region"        = var.region
        }
      }
    }
  ])
  depends_on = [
    null_resource.build_collector
  ]
}

resource "aws_ecs_task_definition" "datapipeline" {
  family                   = "ccm-${var.tenant}-family-datapipeline"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.container_cpu
  memory                   = var.container_memory
  container_definitions = jsonencode([
    {
      name  = "ccm-${var.tenant}-task-datapipeline"
      image = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.region}.amazonaws.com/datapipeline-${var.tenant}:latest"
      essential = true
      cpu = 0
      mountPoints      = []
      systemControls   = []
      volumesFrom      = []
      secrets = [
        {
          name      = "POSTGRES_PASSWORD"
          valueFrom = aws_ssm_parameter.db_secret.arn
        }
      ]
      environment = [
        {
          name  = "ALERT_SLACK_WEBHOOK"
          value = var.alert_slack_webhook
        },
        {
          name  = "ALERT_SLACK_TOKEN"
          value = var.alert_slack_token
        },
        {
          name  = "ALERT_SLACK_CHANNEL"
          value = var.alert_slack_channel
        },
        {
          name  = "POSTGRES_ENDPOINT"
          value = aws_db_instance.database.address
        },
        {
          name  = "POSTGRES_USERNAME"
          value = var.db_username
        },
        {
          name  = "POSTGRES_SCHEMA"
          value = "public"
        },
        {
          name  = "POSTGRES_DATABASE"
          value = aws_db_instance.database.db_name
        },
        {
          name  = "POSTGRES_PORT"
          value = tostring(aws_db_instance.database.port)
        },
        {
          name  = "_TENANT"
          value = var.tenant
        },
        {
          name = "_TRIGGER_REBUILD"
          value = md5(join("", 
            [for f in fileset("${path.module}/../../datapipeline", "**/*") : filemd5("${path.module}/../../datapipeline/${f}")],
          ))
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.log_group.name
          "awslogs-stream-prefix" = var.tenant
          "awslogs-region"        = var.region
        }
      }
    }
  ])
  depends_on = [
    null_resource.build_datapipeline
  ]
}

resource "aws_ecs_task_definition" "dashboard" {
  family                   = "ccm-${var.tenant}-family-dashboard"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.container_cpu
  memory                   = var.container_memory
  container_definitions = jsonencode([
    {
      name  = "ccm-${var.tenant}-task-dashboard"
      image = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.region}.amazonaws.com/dashboard-${var.tenant}:latest"
      essential = true
      cpu = 0
      mountPoints      = []
      systemControls   = []
      volumesFrom      = []
      secrets = [
        {
          name      = "POSTGRES_PASSWORD"
          valueFrom = aws_ssm_parameter.db_secret.arn
        }
      ]
      environment = [
        {
          name  = "POSTGRES_ENDPOINT"
          value = aws_db_instance.database.address
        },
        {
          name  = "POSTGRES_USERNAME"
          value = var.db_username
        },
        {
          name  = "POSTGRES_SCHEMA"
          value = "public"
        },
        {
          name  = "POSTGRES_DATABASE"
          value = aws_db_instance.database.db_name
        },
        {
          name      = "POSTGRES_PORT"
          valueFrom = tostring(aws_db_instance.database.port)
        },
        {
          name  = "_TENANT"
          value = var.tenant
        },
        {
          name = "_TRIGGER_REBUILD"
          value = md5(join("", 
            [for f in fileset("${path.module}/../../dashboard", "**/*") : filemd5("${path.module}/../../dashboard/${f}")],
          ))
        }
      ],
      portMappings = [{
        containerPort = 8080
        hostPort      = 8080
        protocol      = "tcp"
      }],
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.log_group.name
          "awslogs-stream-prefix" = var.tenant
          "awslogs-region"        = var.region
        }
      }
    }
  ])
  tags = var.tags
  depends_on = [
    null_resource.build_dashboard
  ]
}

# Traffic to the ECS cluster should only come from the ALB
resource "aws_security_group" "ecs_tasks" {
  name        = "ccm-${var.tenant}-securitygroup-web-to-alb"
  description = "ALB security group - internet access"
  vpc_id      = var.aws_vpc_id

  ingress {
    protocol        = "tcp"
    from_port       = 8080
    to_port         = 8080
    security_groups = [aws_security_group.sg_alb.id]
  }

  ingress {
    protocol    = "tcp"
    from_port   = 8080
    to_port     = 8080
    cidr_blocks = var.dashboard_cidr_inbound_allow
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = var.tags
}

resource "aws_ecs_service" "dashboard" {
  name            = "ccm-${var.tenant}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.dashboard.arn
  desired_count   = 1
  capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT" # You may want to change this to FARGATE if you don't want this workload interrupted
    weight            = 1
  }

  network_configuration {
    subnets          = var.aws_container_subnets
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = true
  }

  force_new_deployment = true

  #  load_balancer {
  #    target_group_arn = aws_lb_target_group.tg.arn
  #    container_name = "ccm-${var.tenant}-task-dashboard"
  #    container_port = 8080
  #  }
  tags = var.tags
}