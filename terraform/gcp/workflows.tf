resource "google_workflows_workflow" "workflow" {
  name            = "ccm-${var.tenant}-workflow"
  region          = var.region
  service_account = google_service_account.cloud_run_sa.email

  source_contents = <<-EOF
    main:
        steps:
            - run_collector:
                call: googleapis.run.v1.namespaces.jobs.run
                args:
                    name: "namespaces/${var.gcp_project_id}/jobs/ccm-${var.tenant}-collector"
                    location: "${var.region}"
                result: collector_execution
            - run_dbt:
                call: googleapis.run.v1.namespaces.jobs.run
                args:
                    name: "namespaces/${var.gcp_project_id}/jobs/ccm-${var.tenant}-datapipeline"
                    location: "${var.region}"
    EOF

  call_log_level = "LOG_ALL_CALLS"

  depends_on = [
    google_cloud_run_v2_job.collector,
    google_cloud_run_v2_job.datapipeline
  ]
}

