# This configuration sets up the required providers and enables necessary APIs for GCP.
terraform {
  required_providers {

    # Required providers for GCP and other resources
    time = {
      source  = "hashicorp/time"
      version = "~> 0.10"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 6.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}
# Configure the Google Cloud provider with project and region
provider "google" {
  project = var.gcp_project_id
  region  = var.region
}

provider "google-beta" {
  project = var.gcp_project_id
  region  = var.region
}
