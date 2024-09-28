terraform {
  required_version = ">= 1.2.0"
}

resource "local_file" "example_file" {
  content  = "This is a simulated server configuration."
  filename = "${path.module}/example_server.txt"
}

output "file_path" {
  value = local_file.example_file.filename
}

terraform {
  required_providers {
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
  }
}

resource "null_resource" "simulated_server" {
  provisioner "local-exec" {
    command = "echo 'Simulated server created at $(date)' > simulated_server.txt"
  }

  triggers = {
    always_run = "${timestamp()}"
  }
}

output "simulated_server_file" {
  value = null_resource.simulated_server.id
}
