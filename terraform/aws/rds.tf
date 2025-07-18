resource "aws_db_instance" "database" {
  identifier              = "ccm-${var.tenant}-rds"
  instance_class          = var.db_instance_size
  allocated_storage       = var.db_storage
  engine                  = "postgres"
  engine_version          = var.db_version
  username                = var.db_username
  password                = aws_ssm_parameter.db_secret.value
  db_subnet_group_name    = aws_db_subnet_group.database_sg.name
  vpc_security_group_ids  = [aws_security_group.rds_sg.id]
  backup_retention_period = 3
  parameter_group_name    = aws_db_parameter_group.database_pg.name
  db_name                 = "${var.db_name}${var.tenant}"
  tags                    = var.tags
  skip_final_snapshot     = true
  publicly_accessible     = var.db_public_facing
}

resource "aws_db_parameter_group" "database_pg" {
  name   = "ccm-${var.tenant}-parameter-group"
  family = "postgres17"
  tags   = var.tags
}

resource "aws_db_subnet_group" "database_sg" {
  name       = "ccm-${var.tenant}-subnet-group"
  subnet_ids = var.aws_rds_subnet_ids
  tags       = var.tags
}

resource "aws_security_group" "rds_sg" {
  name        = "ccm-${var.tenant}-securitygroup-ecs-to-rds"
  description = "ECS to RDS internal traffic"
  vpc_id      = var.aws_vpc_id

  ingress {
    protocol        = "tcp"
    from_port       = 5432
    to_port         = 5432
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  ingress {
    protocol    = "tcp"
    from_port   = 5432
    to_port     = 5432
    cidr_blocks = var.db_cidr_inbound_allow
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = var.tags
}