output "url" {
  value = var.public_url != "" ? var.public_url : "http://${var.bind_ip}:${var.port}"
}
