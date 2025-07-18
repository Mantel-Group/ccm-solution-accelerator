# Local values
locals {
  artifact_registry_name = "ccm-${var.tenant}-registry"
}

# Artifact Registry for container images
resource "google_artifact_registry_repository" "container_registry" {
  location      = var.region
  repository_id = local.artifact_registry_name
  description   = "Container registry for ${var.tenant} continuous assurance"
  format        = "DOCKER"
  labels        = var.tags
  depends_on    = [google_project_service.artifactregistry, time_sleep.all_apis_ready]

  cleanup_policies {
    id     = "keep-recent-untagged"
    action = "DELETE"

    condition {
      tag_state  = "UNTAGGED"
      older_than = "86400s" # 1 day in seconds
    }
  }

  cleanup_policies {
    id     = "keep-recent-tagged"
    action = "DELETE"

    condition {
      tag_state  = "TAGGED"
      older_than = "604800s" # 7 days for tagged images (optional, adjust as needed)
    }
  }
}

# IAM binding for Cloud Build to push images
resource "google_artifact_registry_repository_iam_binding" "cloudbuild_writer" {
  location   = google_artifact_registry_repository.container_registry.location
  repository = google_artifact_registry_repository.container_registry.name
  role       = "roles/artifactregistry.writer"

  members = [
    "serviceAccount:${data.google_project.current.number}@cloudbuild.gserviceaccount.com",
  ]
  depends_on = [time_sleep.all_apis_ready]
}

# IAM binding for Cloud Run to pull images
resource "google_artifact_registry_repository_iam_binding" "cloudrun_reader" {
  location   = google_artifact_registry_repository.container_registry.location
  repository = google_artifact_registry_repository.container_registry.name
  role       = "roles/artifactregistry.reader"

  members = [
    "serviceAccount:${data.google_project.current.number}-compute@developer.gserviceaccount.com",
  ]
  depends_on = [time_sleep.all_apis_ready]
}
