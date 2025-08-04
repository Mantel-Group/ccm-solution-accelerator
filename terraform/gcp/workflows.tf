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
                    name: "namespaces/${var.gcp_project_id}/jobs/collector"
                    location: "${var.region}"
                result: collector_execution
            - run_dbt:
                call: googleapis.run.v1.namespaces.jobs.run
                args:
                    name: "namespaces/${var.gcp_project_id}/jobs/dbt"
                    location: "${var.region}"
    EOF

  depends_on = [
    google_cloud_run_v2_job.collector,
    google_cloud_run_v2_job.dbt
  ]
}

