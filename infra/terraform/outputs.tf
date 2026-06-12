output "bigtable_instance_name" {
  description = "Nom de l'instance Bigtable"
  value       = google_bigtable_instance.price_intelligence.name
}

output "gke_cluster_name" {
  description = "Nom du cluster GKE"
  value       = google_container_cluster.price_intelligence.name
}

output "gke_cluster_endpoint" {
  description = "Endpoint du cluster GKE"
  value       = google_container_cluster.price_intelligence.endpoint
  sensitive   = true
}

output "artifact_registry_url" {
  description = "URL du registre Docker"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_name}"
}

output "app_sa_email" {
  description = "Email du Service Account applicatif"
  value       = google_service_account.app_sa.email
}

output "composer_bucket" {
  description = "Bucket GCS du Composer pour les DAGs"
  value       = google_composer_environment.airflow.config[0].dag_gcs_prefix
}

output "terraform_state_bucket" {
  description = "Bucket GCS pour le state Terraform"
  value       = google_storage_bucket.terraform_state.name
}