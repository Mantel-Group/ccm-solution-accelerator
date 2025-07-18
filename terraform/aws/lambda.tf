resource "aws_iam_role" "lambda_role" {
  name               = "${var.tenant}-lambda-role"
  description        = "IAM role for Lambda that finds latest ECS dashboard task public IP"
  assume_role_policy = data.aws_iam_policy_document.lambda_trust.json
  tags               = var.tags
}

data "aws_iam_policy_document" "lambda_trust" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "lambda_policy" {
  statement {
    sid    = "AllowEcsListAndDescribe"
    effect = "Allow"
    actions = [
      "ecs:ListTasks",
      "ecs:DescribeTasks"
    ]
    resources = ["*"] # ListTasks cannot be resource‑scoped
  }

  statement {
    sid       = "AllowEc2DescribeENIs"
    effect    = "Allow"
    actions   = ["ec2:DescribeNetworkInterfaces"]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "lambda_inline" {
  name   = "${var.tenant}-lambda-inline"
  role   = aws_iam_role.lambda_role.id
  policy = data.aws_iam_policy_document.lambda_policy.json
}

resource "aws_iam_role_policy_attachment" "basic_lambda" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda/main.py"
  output_path = "${path.module}/build/dashboard.zip"
}

resource "aws_lambda_function" "dashboard_redirect" {
  function_name = "${var.tenant}-dashboard-redirect"
  role          = aws_iam_role.lambda_role.arn
  runtime       = "python3.12"
  handler       = "main.lambda_handler"

  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = filebase64sha256(data.archive_file.lambda_zip.output_path)

  timeout     = 10
  memory_size = 128

  environment {
    variables = {
      TENANT = var.tenant
    }
  }

  tags = var.tags
}

resource "aws_lambda_function_url" "dashboard_redirect" {
  function_name      = aws_lambda_function.dashboard_redirect.function_name
  authorization_type = "NONE"
}
