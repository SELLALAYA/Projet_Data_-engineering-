variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "project-32a82952-90fa-4dd7-b9c"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "europe-west1"
}

variable "zone" {
  description = "GCP Zone"
  type        = string
  default     = "europe-west1-b"
}

variable "bigtable_instance_name" {
  description = "Nom de l'instance Bigtable"
  type        = string
  default     = "price-intelligence-bt"
}

variable "gke_cluster_name" {
  description = "Nom du cluster GKE"
  type        = string
  default     = "price-intelligence-gke"
}

variable "artifact_registry_name" {
  description = "Nom du registre Docker"
  type        = string
  default     = "price-intelligence-registry"
}

variable "composer_env_name" {
  description = "Nom de l'environnement Cloud Composer"
  type        = string
  default     = "price-intelligence-composer"
}