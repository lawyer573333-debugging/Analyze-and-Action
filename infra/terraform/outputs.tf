output "cloud_run_url" {
  value = google_cloud_run_v2_service.backend_api.uri
}

output "database_ip" {
  value = google_sql_database_instance.postgres_instance.public_ip_address
}

output "redis_host" {
  value = google_redis_instance.cache.host
}
