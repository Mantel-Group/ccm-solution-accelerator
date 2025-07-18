resource "aws_ecr_repository" "collector" {
  name = "collector-${var.tenant}"
  tags = var.tags
}

resource "aws_ecr_repository" "dashboard" {
  name = "dashboard-${var.tenant}"
  tags = var.tags
}

resource "aws_ecr_repository" "datapipeline" {
  name = "datapipeline-${var.tenant}"
  tags = var.tags
}

resource "aws_ecr_lifecycle_policy" "collector_policy" {
  repository = aws_ecr_repository.collector.name

  policy = <<EOF
{
    "rules": [
        {
            "rulePriority": 1,
            "description": "Only keep 1 image",
            "selection": {
                "tagStatus": "untagged",
                "countType": "sinceImagePushed",
                "countUnit" : "days",
                "countNumber": 1
            },
            "action": {
                "type": "expire"
            }
        }
    ]
}
EOF
}

resource "aws_ecr_lifecycle_policy" "datapipeline_policy" {
  repository = aws_ecr_repository.datapipeline.name

  policy = <<EOF
{
    "rules": [
        {
            "rulePriority": 1,
            "description": "Only keep 1 image",
            "selection": {
                "tagStatus": "untagged",
                "countType": "sinceImagePushed",
                "countUnit" : "days",
                "countNumber": 1
            },
            "action": {
                "type": "expire"
            }
        }
    ]
}
EOF
}

resource "aws_ecr_lifecycle_policy" "dashboard_policy" {
  repository = aws_ecr_repository.dashboard.name

  policy = <<EOF
{
    "rules": [
        {
            "rulePriority": 1,
            "description": "Only keep 1 image",
            "selection": {
                "tagStatus": "untagged",
                "countType": "sinceImagePushed",
                "countUnit" : "days",
                "countNumber": 1
            },
            "action": {
                "type": "expire"
            }
        }
    ]
}
EOF
}

