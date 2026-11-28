terraform {
  required_version = ">= 1.9.0"
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "docker" {
  host = var.docker_host
}

resource "random_password" "db" {
  length  = 20
  special = false
}

resource "docker_network" "catshop" {
  name = "catshop-net"
}

resource "docker_volume" "db_data" {
  name = "catshop-db-data"
}

resource "docker_image" "postgres" {
  name         = "postgres:16-alpine"
  keep_locally = true
}

resource "docker_image" "nginx" {
  name         = "nginx:1.27-alpine"
  keep_locally = true
}

resource "docker_container" "db" {
  name     = "catshop-db"
  image    = docker_image.postgres.image_id
  hostname = "db"

  env = [
    "POSTGRES_DB=catshop",
    "POSTGRES_USER=catshop",
    "POSTGRES_PASSWORD=${random_password.db.result}",
  ]

  volumes {
    volume_name    = docker_volume.db_data.name
    container_path = "/var/lib/postgresql/data"
  }

  networks_advanced {
    name    = docker_network.catshop.name
    aliases = ["db"]
  }

  restart = "unless-stopped"
}

resource "docker_container" "web" {
  count    = var.replicas
  name     = "catshop-web-${count.index}"
  image    = docker_image.nginx.image_id
  hostname = "catshop-web-${count.index}"

  upload {
    content = file("${path.module}/web.conf")
    file    = "/etc/nginx/conf.d/default.conf"
  }

  networks_advanced {
    name    = docker_network.catshop.name
    aliases = ["catshop-web-${count.index}"]
  }

  restart = "unless-stopped"
}

resource "docker_container" "proxy" {
  name  = "catshop-proxy"
  image = docker_image.nginx.image_id

  upload {
    content = templatefile("${path.module}/nginx.conf.tftpl", {
      web_hosts = docker_container.web[*].name
    })
    file = "/etc/nginx/conf.d/default.conf"
  }

  ports {
    internal = 80
    external = var.port
    ip       = var.bind_ip
  }

  networks_advanced {
    name = docker_network.catshop.name
  }

  restart = "unless-stopped"
}
