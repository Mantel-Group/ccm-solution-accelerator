# Build and push the collector service container image
resource "null_resource" "build_collector" {
  triggers = {
    collector = md5(join("", [
      for f in fileset("${path.module}/../../collector", "**/*") : filemd5("${path.module}/../../collector/${f}")
    ]))
  }

  provisioner "local-exec" {
    working_dir = "${path.module}/../../collector"
    command     = <<EOT
      gcloud auth configure-docker ${var.region}-docker.pkg.dev --quiet
      docker build --platform linux/amd64 -t ${var.region}-docker.pkg.dev/${var.gcp_project_id}/${local.artifact_registry_name}/collector:latest . || exit 1
      docker push ${var.region}-docker.pkg.dev/${var.gcp_project_id}/${local.artifact_registry_name}/collector:latest
    EOT
  }

  depends_on = [
    google_artifact_registry_repository.container_registry,
    google_project_service.artifactregistry,
    time_sleep.all_apis_ready
  ]
}

# Build and push the datapipeline service container image
resource "null_resource" "build_datapipeline" {
  triggers = {
    datapipeline = md5(join("", [
      for f in fileset("${path.module}/../../datapipeline", "**/*") : filemd5("${path.module}/../../datapipeline/${f}")
    ]))
  }

  provisioner "local-exec" {
    working_dir = "${path.module}/../../datapipeline"
    command     = <<EOT
      gcloud auth configure-docker ${var.region}-docker.pkg.dev --quiet
      docker build --platform linux/amd64 -t ${var.region}-docker.pkg.dev/${var.gcp_project_id}/${local.artifact_registry_name}/datapipeline:latest . || exit 1
      docker push ${var.region}-docker.pkg.dev/${var.gcp_project_id}/${local.artifact_registry_name}/datapipeline:latest
    EOT
  }

  depends_on = [
    google_artifact_registry_repository.container_registry,
    google_project_service.artifactregistry,
    time_sleep.all_apis_ready
  ]
}

# Build and push the dashboard service container image
resource "null_resource" "build_dashboard" {
  triggers = {
    dashboard = md5(join("", [
      for f in fileset("${path.module}/../../dashboard", "**/*") : filemd5("${path.module}/../../dashboard/${f}")
    ]))
  }

  provisioner "local-exec" {
    working_dir = "${path.module}/../../dashboard"
    command     = <<EOT
      gcloud auth configure-docker ${var.region}-docker.pkg.dev --quiet
      docker build --platform linux/amd64 -t ${var.region}-docker.pkg.dev/${var.gcp_project_id}/${local.artifact_registry_name}/dashboard:latest . || exit 1
      docker push ${var.region}-docker.pkg.dev/${var.gcp_project_id}/${local.artifact_registry_name}/dashboard:latest
    EOT
  }

  depends_on = [
    google_artifact_registry_repository.container_registry,
    google_project_service.artifactregistry,
    time_sleep.all_apis_ready
  ]
}
