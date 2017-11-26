# PyTerraBackTYL
## About:
PyTerraBackTYL is a generic HTTP/REST backend for storing your Terraform state file, `terraform.tfstate`.

## Setup:
The Below instructions are abbreviated and assume that you plan to use the default GitBackend module.
More complete installation documentation will be created as this project matures.

### Requirements:
- Python 3.6.2 - other versions are untested but are expected to work well.
  - Flask
  - Yaml
  - Json
  - GitPython (requires that the OS has `git` installed)
- Git repository to hold the `terraform.tfstate` file and related files.
- User account to run the PyTerraBackTYL service with SSH keypair.

### High-level installation instructions:
- Install Python3 on the machine running the service.
- `pip3 install` the required libraries listed above.
- Log in as the user that will run the PyTerraBackTYL service.
- Clone the master branch of the PyTerraBackTYL repository into the target
- Generate an SSH keypair for the service user if needed.
- Create a Git repository to store your `terraform.tfstate` file in.
- Add the SSH key to the Git repository to enable clone, commit, and push privileges.
- Modify `config.yaml`
  - Set `GIT_REPOSITORY` to your newly created git repository.
  - Set `BACKEND_SERVICE_IP` - If you're unsure what to use, set this to `0.0.0.0`.
  - Read through the configuration descriptions and make any additional changes.
- Fire up the service with something like, `nohup python3 pyterrabacktyl.py 2>&1 > service.log &`
- Test the service with `curl http://localhost:2442/state; echo` (note that the current implementation of this endpoint does not accurately reflect service health).
- Update one of your Terraform projects to point at the HTTP backend. For example,
```buildoutcfg
terraform {
  backend "http" {
    address = "http://localhost:2442/?env=DEVTEST"
    lock_address = "http://localhost:2442/lock?env=DEVTEST"
    unlock_address = "http://localhost:2442/unlock?env=DEVTEST"
  }
}
```
- **WARNING**: Note the `?env=SOME_ENVIRONMENT` at the end of the url. This is how PyTerraBackTYL identifies separate projects. There's no guardrails around this. **Make sure this value is unique for each seaparate environemnt!**
- Rerun `terraform init` to use the backend service. Say 'yes' at the prompt if you wish to copy the existing terraform.tfstate file to the HTTP backend.

## But I don't want to use Git as a backend:
That's fine. Subclass `abc_tylstore.TYLStore`, implement the required functions, drop your module into the `backends` directory, update your `config.yaml` to point at your new module, and try not to break production in the process of testing.
