terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.80"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Artifact Registry for Docker images
resource "google_artifact_registry_repository" "backend_repo" {
  location      = var.region
  repository_id = "insight-to-action-backend"
  description   = "Docker repository for the FastAPI backend"
  format        = "DOCKER"
}

# Cloud SQL PostgreSQL instance (Production HA)
resource "google_sql_database_instance" "postgres_instance" {
  name             = "insight-to-action-db"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier              = "db-custom-4-16384" # 4 vCPU, 16GB RAM as per architecture
    availability_type = "REGIONAL" # High Availability
    disk_size         = 50
    
    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
    }
  }
  
  deletion_protection = false # Set to true in real production
}

resource "google_sql_database" "database" {
  name     = "insight_to_action"
  instance = google_sql_database_instance.postgres_instance.name
}

resource "google_sql_user" "users" {
  name     = "admin"
  instance = google_sql_database_instance.postgres_instance.name
  password = var.db_password
}

# Cloud Memorystore (Redis)
resource "google_redis_instance" "cache" {
  name           = "insight-to-action-cache"
  tier           = "STANDARD_HA"
  memory_size_gb = 2
  region         = var.region
}

# Cloud Storage for Documents
resource "google_storage_bucket" "documents" {
  name          = "${var.project_id}-documents"
  location      = var.region
  force_destroy = false

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }
}

# Cloud Run Backend Service
resource "google_cloud_run_v2_service" "backend_api" {
  name     = "insight-to-action-api"
  location = var.region

  template {
    scaling {
      min_instance_count = 1
      max_instance_count = 10
    }

    containers {
      image = "us-docker.pkg.dev/cloudrun/container/hello" # Placeholder until CI/CD pushes image

      resources {
        limits = {
          cpu    = "2"
          memory = "2Gi"
        }
      }
      
      env {
        name  = "POSTGRES_SERVER"
        value = google_sql_database_instance.postgres_instance.public_ip_address # Prefer private IP in secure setup
      }
      env {
        name  = "REDIS_URL"
        value = "redis://${google_redis_instance.cache.host}:${google_redis_instance.cache.port}"
      }
    }
  }
}
