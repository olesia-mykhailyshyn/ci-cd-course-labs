variable "docker_host" {
  type    = string
  default = "unix:///var/run/docker.sock"
}

variable "port" {
  type    = number
  default = 8080
}

variable "bind_ip" {
  type    = string
  default = "127.0.0.1"
}

variable "public_url" {
  type    = string
  default = ""
}

variable "replicas" {
  type    = number
  default = 2
}
