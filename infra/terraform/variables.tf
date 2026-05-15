variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "us-central1"
}

variable "db_password" {
  description = "The PostgreSQL user password"
  type        = string
  sensitive   = true
}
