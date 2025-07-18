resource "null_resource" "build_collector" {
  triggers = {
    collector = md5(join("", [
      for f in fileset("${path.module}/../../collector", "**/*") : filemd5("${path.module}/../../collector/${f}")
    ]))
  }

  provisioner "local-exec" {
    working_dir = "${path.module}/../../collector"
    interpreter = ["/bin/sh", "-c"]
    command     = <<-EOT
      docker build --platform linux/amd64 -t "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.region}.amazonaws.com/collector-${var.tenant}:latest" . || exit 1
      login_cmd=$(aws ecr get-login-password --region "${var.region}")
      echo "$login_cmd" | docker login --username AWS --password-stdin "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.region}.amazonaws.com"
      docker push "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.region}.amazonaws.com/collector-${var.tenant}:latest"
    EOT
  }

  depends_on = [
    aws_ecr_repository.collector
  ]
}

resource "null_resource" "build_datapipeline" {
  triggers = {
    datapipeline = md5(join("", [
      for f in fileset("${path.module}/../../datapipeline", "**/*") : filemd5("${path.module}/../../datapipeline/${f}")
    ]))
  }

  provisioner "local-exec" {
    working_dir = "${path.module}/../../datapipeline"
    interpreter = ["/bin/sh", "-c"]
    command     = <<-EOT
      docker build --platform linux/amd64 -t "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.region}.amazonaws.com/datapipeline-${var.tenant}:latest" . || exit 1
      login_cmd=$(aws ecr get-login-password --region "${var.region}")
      echo "$login_cmd" | docker login --username AWS --password-stdin "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.region}.amazonaws.com"
      docker push "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.region}.amazonaws.com/datapipeline-${var.tenant}:latest"
    EOT
  }

  depends_on = [
    aws_ecr_repository.datapipeline
  ]
}

resource "null_resource" "build_dashboard" {
  triggers = {
    dashboard = md5(join("", [
      for f in fileset("${path.module}/../../dashboard", "**/*") : filemd5("${path.module}/../../dashboard/${f}")
    ]))

    credential_changes = md5("${var.dashboard_username}:${var.dashboard_password}")
  }

  provisioner "local-exec" {
    working_dir = "${path.module}/../../dashboard"
    interpreter = ["/bin/sh", "-c"]
    command     = <<-EOT
      docker build --build-arg DEFAULT_USER="${var.dashboard_username}" --build-arg DEFAULT_PASSWORD="${var.dashboard_password}" --platform linux/amd64 -t "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.region}.amazonaws.com/dashboard-${var.tenant}:latest" . || exit 1
      login_cmd=$(aws ecr get-login-password --region "${var.region}")
      echo "$login_cmd" | docker login --username AWS --password-stdin "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.region}.amazonaws.com"
      docker push "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.region}.amazonaws.com/dashboard-${var.tenant}:latest"
    EOT
  }

  depends_on = [
    aws_ecr_repository.dashboard
  ]
}