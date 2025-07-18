# Build and push collector image
resource "null_resource" "build_collector" {
  triggers = {
    collector = md5(join("", [
      for f in fileset("${path.module}/../../collector", "**/*") : filemd5("${path.module}/../../collector/${f}")
    ]))
  }

  provisioner "local-exec" {
    working_dir = "${path.module}/../../collector"
    command     = <<-EOT
      az acr login -n ${azurerm_container_registry.acr.name}
      docker build --platform linux/amd64 -t "${azurerm_container_registry.acr.login_server}/collector:latest" . || exit 1
      docker push "${azurerm_container_registry.acr.login_server}/collector:latest"
    EOT
  }

  depends_on = [
    azurerm_container_registry.acr
  ]
}

# Build and push datapipeline image
resource "null_resource" "build_datapipeline" {
  triggers = {
    collector = md5(join("", [
      for f in fileset("${path.module}/../../datapipeline", "**/*") : filemd5("${path.module}/../../datapipeline/${f}")
    ]))
  }

  provisioner "local-exec" {
    working_dir = "${path.module}/../../datapipeline"
    command     = <<EOT
      az acr login -n ${azurerm_container_registry.acr.name}
      docker build --platform linux/amd64 -t "${azurerm_container_registry.acr.login_server}/datapipeline:latest" . || exit 1
      docker push "${azurerm_container_registry.acr.login_server}/datapipeline:latest"
    EOT
  }

  depends_on = [
    azurerm_container_registry.acr
  ]
}

# Build and push dashboard image
resource "null_resource" "build_dashboard" {
  triggers = {
    collector = md5(join("", [
      for f in fileset("${path.module}/../../dashboard", "**/*") : filemd5("${path.module}/../../dashboard/${f}")
    ]))

    credential_changes = md5("${var.dashboard_username}:${var.dashboard_password}")
  }

  provisioner "local-exec" {
    working_dir = "${path.module}/../../dashboard"
    command     = <<EOT
      az acr login -n ${azurerm_container_registry.acr.name}
      docker build --platform linux/amd64 --build-arg DEFAULT_USER="${var.dashboard_username}" --build-arg DEFAULT_PASSWORD="${var.dashboard_password}" -t "${azurerm_container_registry.acr.login_server}/dashboard:latest" . || exit 1
      docker push "${azurerm_container_registry.acr.login_server}/dashboard:latest"
    EOT
  }

  depends_on = [
    azurerm_container_registry.acr
  ]
}