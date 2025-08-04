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

resource "google_cloud_scheduler_job" "workflow_schedule" {
  name      = "ccm-${var.tenant}-workflow_schedule"
  schedule  = var.cron_schedule
  time_zone = "Australia/Sydney"
  region    = var.region

  http_target {
    http_method = "POST"
    uri         = "https://workflowexecutions.googleapis.com/v1/projects/${var.gcp_project_id}/locations/${var.region}/workflows/ccm-${var.tenant}-workflow/executions"

    oauth_token {
      service_account_email = google_service_account.cloud_run_sa.email
    }
  }

  depends_on = [
    google_workflows_workflow.workflow,
    google_project_service.cloudscheduler,
    google_project_iam_member.scheduler_run_invoker,
    time_sleep.all_apis_ready
  ]
}
