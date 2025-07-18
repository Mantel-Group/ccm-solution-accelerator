# Enable required GCP APIs in sequence with delays

# CORE APIs - These must be enabled first and in sequence
# Enable serviceusage.googleapis.com (required for enabling other APIs)
resource "google_project_service" "serviceusage" {
  service            = "serviceusage.googleapis.com"
  disable_on_destroy = false
}

resource "time_sleep" "after_serviceusage" {
  create_duration = "10s"
  depends_on      = [google_project_service.serviceusage]
}

# Enable cloudresourcemanager.googleapis.com 
resource "google_project_service" "cloudresourcemanager" {
  service            = "cloudresourcemanager.googleapis.com"
  disable_on_destroy = false
  depends_on         = [time_sleep.after_serviceusage]
}

resource "time_sleep" "after_cloudresourcemanager" {
  create_duration = "10s"
  depends_on      = [google_project_service.cloudresourcemanager]
}

# Enable iam.googleapis.com
resource "google_project_service" "iam" {
  service            = "iam.googleapis.com"
  disable_on_destroy = false
  depends_on         = [time_sleep.after_cloudresourcemanager]
}

# Longer wait after core APIs to ensure propagation
resource "time_sleep" "core_apis_ready" {
  create_duration = "30s"
  depends_on      = [google_project_service.iam]
}

# REMAINING APIs - Can be enabled after core APIs are ready
resource "google_project_service" "compute" {
  service            = "compute.googleapis.com"
  disable_on_destroy = false
  depends_on         = [time_sleep.core_apis_ready]
}

resource "google_project_service" "artifactregistry" {
  service            = "artifactregistry.googleapis.com"
  disable_on_destroy = false
  depends_on         = [time_sleep.core_apis_ready]
}

resource "google_project_service" "run" {
  service            = "run.googleapis.com"
  disable_on_destroy = false
  depends_on         = [time_sleep.core_apis_ready]
}

resource "google_project_service" "sqladmin" {
  service            = "sqladmin.googleapis.com"
  disable_on_destroy = false
  depends_on         = [time_sleep.core_apis_ready]
}

resource "google_project_service" "secretmanager" {
  service            = "secretmanager.googleapis.com"
  disable_on_destroy = false
  depends_on         = [time_sleep.core_apis_ready]
}

resource "google_project_service" "cloudbuild" {
  service            = "cloudbuild.googleapis.com"
  disable_on_destroy = false
  depends_on         = [time_sleep.core_apis_ready]
}

resource "google_project_service" "cloudscheduler" {
  service            = "cloudscheduler.googleapis.com"
  disable_on_destroy = false
  depends_on         = [time_sleep.core_apis_ready]
}

resource "google_project_service" "servicenetworking" {
  service            = "servicenetworking.googleapis.com"
  disable_on_destroy = false
  depends_on         = [time_sleep.core_apis_ready]
}

resource "google_project_service" "vpcaccess" {
  service            = "vpcaccess.googleapis.com"
  disable_on_destroy = false
  depends_on         = [time_sleep.core_apis_ready]
}

# Final readiness indicator for other resources to depend on
resource "time_sleep" "all_apis_ready" {
  create_duration = "120s"
  depends_on = [
    google_project_service.compute,
    google_project_service.artifactregistry,
    google_project_service.run,
    google_project_service.sqladmin,
    google_project_service.secretmanager,
    google_project_service.cloudbuild,
    google_project_service.cloudscheduler,
    google_project_service.servicenetworking,
    google_project_service.vpcaccess
  ]
}
