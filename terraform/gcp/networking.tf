# VPC Network and Subnet Configuration
resource "google_compute_network" "vpc" {
  name                    = "${var.tenant}-vpc"
  auto_create_subnetworks = false
  routing_mode            = "REGIONAL"
  depends_on              = [time_sleep.all_apis_ready]
}

# Subnet for database resources
resource "google_compute_subnetwork" "database_subnet" {
  name          = "${var.tenant}-database-subnet"
  ip_cidr_range = var.gcp_database_subnet_cidr
  region        = var.region
  network       = google_compute_network.vpc.id

  # Enable private Google access for services
  private_ip_google_access = true
  depends_on               = [time_sleep.all_apis_ready]
}

# Subnet for container resources
resource "google_compute_subnetwork" "container_subnet" {
  name          = "${var.tenant}-container-subnet"
  ip_cidr_range = var.gcp_container_subnet_cidr
  region        = var.region
  network       = google_compute_network.vpc.id

  # Enable private Google access for services
  private_ip_google_access = true
  depends_on               = [time_sleep.all_apis_ready]
}

# Firewall rule - allow container to database communication
resource "google_compute_firewall" "allow_container_to_database" {
  name    = "${var.tenant}-allow-container-to-database"
  network = google_compute_network.vpc.name

  allow {
    protocol = "tcp"
    ports    = ["5432"]
  }

  source_ranges = [var.gcp_container_subnet_cidr]
  target_tags   = ["ccm-${var.tenant}-database"]
  depends_on    = [time_sleep.all_apis_ready]
}

# Firewall rule - allow internal container communication
resource "google_compute_firewall" "allow_container_internal" {
  name    = "${var.tenant}-allow-container-internal"
  network = google_compute_network.vpc.name

  allow {
    protocol = "tcp"
    ports    = ["80", "443", "8080"]
  }

  allow {
    protocol = "icmp"
  }

  source_ranges = [var.gcp_container_subnet_cidr]
  target_tags   = ["ccm-${var.tenant}-container"]
  depends_on    = [time_sleep.all_apis_ready]
}

# Firewall rule - allow external access to dashboard
resource "google_compute_firewall" "allow_dashboard_external" {
  name    = "${var.tenant}-allow-dashboard-external"
  network = google_compute_network.vpc.name

  allow {
    protocol = "tcp"
    ports    = ["80", "443", "8080"]
  }

  source_ranges = var.dashboard_cidr_inbound_allow
  target_tags   = ["ccm-${var.tenant}-dashboard"]
  depends_on    = [time_sleep.all_apis_ready]
}

# Private Service Connect for Cloud SQL
resource "google_compute_global_address" "private_ip_address" {
  name          = "${var.tenant}-private-ip-address"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc.id
  depends_on    = [time_sleep.all_apis_ready]
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
  depends_on              = [time_sleep.all_apis_ready]
}

# VPC Access Connector for Cloud Run to access private resources
resource "google_vpc_access_connector" "connector" {
  name          = "ccm-${var.tenant}-connector"
  ip_cidr_range = "10.${random_integer.vpc_connector_cidr.result}.0.0/28"
  network       = google_compute_network.vpc.name
  region        = var.region
  max_instances = 3
  min_instances = 2

  depends_on = [
    google_project_service.vpcaccess,
    google_compute_network.vpc,
    time_sleep.all_apis_ready
  ]
}

# Random CIDR for VPC connector to avoid conflicts
resource "random_integer" "vpc_connector_cidr" {
  min = 8
  max = 254
}
