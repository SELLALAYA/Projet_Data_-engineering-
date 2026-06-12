terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.0"
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# ─────────────────────────────────────────
# GCS BUCKET — Terraform State
# ─────────────────────────────────────────
resource "google_storage_bucket" "terraform_state" {
  name                        = "tf-state-project-32a82952"
  location                    = var.region
  force_destroy               = true
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }
}

# ─────────────────────────────────────────
# BIGTABLE
# ─────────────────────────────────────────
resource "google_bigtable_instance" "price_intelligence" {
  name                = var.bigtable_instance_name
  deletion_protection = false

  cluster {
    cluster_id   = "${var.bigtable_instance_name}-cluster"
    zone         = var.zone
    num_nodes    = 1
    storage_type = "SSD"
  }
}

resource "google_bigtable_table" "prices" {
  name          = "prices"
  instance_name = google_bigtable_instance.price_intelligence.name
}

resource "google_bigtable_table" "metadata" {
  name          = "metadata"
  instance_name = google_bigtable_instance.price_intelligence.name
}

# ─────────────────────────────────────────
# ARTIFACT REGISTRY
# ─────────────────────────────────────────
resource "google_artifact_registry_repository" "docker_registry" {
  location      = var.region
  repository_id = var.artifact_registry_name
  format        = "DOCKER"
  description   = "Docker registry pour Price Intelligence"
}

# ─────────────────────────────────────────
# GKE CLUSTER
# ─────────────────────────────────────────
resource "google_container_cluster" "price_intelligence" {
  name     = var.gke_cluster_name
  location = var.zone

  initial_node_count = 2

  node_config {
    machine_type = "e2-medium"
    disk_size_gb = 50

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }

  deletion_protection = false
}

# ─────────────────────────────────────────
# CLOUD COMPOSER (Airflow managé)
# ─────────────────────────────────────────
resource "google_composer_environment" "airflow" {
  name   = var.composer_env_name
  region = var.region

  config {
    software_config {
      image_version = "composer-2-airflow-2"
    }
    node_config {
      service_account = google_service_account.app_sa.email
    }
  }
}

# ─────────────────────────────────────────
# SERVICE ACCOUNT APPLICATIF
# ─────────────────────────────────────────
resource "google_service_account" "app_sa" {
  account_id   = "price-intelligence-sa"
  display_name = "Price Intelligence App SA"
}

resource "google_project_iam_member" "app_sa_bigtable" {
  project = var.project_id
  role    = "roles/bigtable.admin"
  member  = "serviceAccount:${google_service_account.app_sa.email}"
}

resource "google_project_iam_member" "app_sa_registry" {
  project = var.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.app_sa.email}"
}

resource "google_project_iam_member" "app_sa_composer" {
  project = var.project_id
  role    = "roles/composer.worker"
  member  = "serviceAccount:${google_service_account.app_sa.email}"
}