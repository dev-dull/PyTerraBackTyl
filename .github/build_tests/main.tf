terraform {
  required_version = ">= 1.2.0"
}

resource "local_file" "test_file" {
  content  = "This is a local file."
  filename = "${path.module}/test.txt"
}

output "file_path" {
  value = local_file.test_file.filename
}

terraform {
  required_providers {
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
  }
}

resource "null_resource" "null_file" {
  provisioner "local-exec" {
    command = "echo Null resource created at $(date) > null_file.txt"
  }

  triggers = {
    always_run = "${timestamp()}"
  }
}

output "null_file_output" {
  value = null_resource.null_file.id
}
