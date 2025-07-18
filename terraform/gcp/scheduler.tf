# Cloud Scheduler jobs to automatically run collector and datapipeline

# Service account for Cloud Scheduler to invoke Cloud Run jobs
resource "google_service_account" "scheduler_sa" {
  account_id   = "ccm-${var.tenant}-scheduler"
  display_name = "Cloud Scheduler Service Account for ${var.tenant}"
  description  = "Service account used by Cloud Scheduler to invoke Cloud Run jobs"
  depends_on   = [time_sleep.all_apis_ready]
}

# Grant permission to invoke Cloud Run jobs
resource "google_project_iam_member" "scheduler_run_invoker" {
  project    = var.gcp_project_id
  role       = "roles/run.invoker"
  member     = "serviceAccount:${google_service_account.scheduler_sa.email}"
  depends_on = [time_sleep.all_apis_ready]
}

# IAM bindings for the scheduler service account
resource "google_project_iam_member" "scheduler_run_developer" {
  project    = var.gcp_project_id
  role       = "roles/run.developer"
  member     = "serviceAccount:${google_service_account.scheduler_sa.email}"
  depends_on = [time_sleep.all_apis_ready]
}

resource "google_project_iam_member" "scheduler_run_viewer" {
  project    = var.gcp_project_id
  role       = "roles/run.viewer"
  member     = "serviceAccount:${google_service_account.scheduler_sa.email}"
  depends_on = [time_sleep.all_apis_ready]
}

# Collector runs first at 6:00 PM
resource "google_cloud_scheduler_job" "collector_schedule" {
  name      = "ccm-${var.tenant}-collector-schedule"
  schedule  = var.cron_schedule
  time_zone = "Australia/Sydney"
  region    = var.region

  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.gcp_project_id}/jobs/ccm-${var.tenant}-collector:run"

    oauth_token {
      service_account_email = google_service_account.scheduler_sa.email
    }
  }

  depends_on = [
    google_project_service.cloudscheduler,
    google_project_iam_member.scheduler_run_invoker,
    time_sleep.all_apis_ready
  ]
}

# Datapipeline runs 6 hours later at 10:00 PM (assuming collector takes < 3 hours)
resource "google_cloud_scheduler_job" "datapipeline_schedule" {
  name      = "ccm-${var.tenant}-datapipeline-schedule"
  schedule  = var.datapipeline_cron_schedule # 10:00 PM daily (4 hours after collector)
  time_zone = "Australia/Sydney"
  region    = var.region

  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.gcp_project_id}/jobs/ccm-${var.tenant}-datapipeline:run"

    oauth_token {
      service_account_email = google_service_account.scheduler_sa.email
    }
  }

  depends_on = [
    google_project_service.cloudscheduler,
    google_project_iam_member.scheduler_run_invoker,
    time_sleep.all_apis_ready
  ]
}
