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

### Detailed installation instructions:
#### Install PyTerraBackTYL:
- SSH to the host you intend to run the PyTerraBackTYL service on.
  - e.g. `ssh user@linuxhost`
- Check if `python3` is installed.
  - e.g. `whereis python3`
- Install Python 3.x if needed
  - RedHat/CentOS ([source](https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-local-programming-environment-on-centos-7)): 
    - Install yum utils: `yum install yum-utils`
    - Install libs/dependencies: `yum groupinstall development`
    - Install the Yum Repo with Python 3.x: `yum -y install https://centos7.iuscommunity.org/ius-release.rpm`
    - Install Python 3.x: `yum -y install python36u python36u-pip`
  - Debian/Ubuntu:
    - Note: This currently installs Python 3.5, PyTerraBackTYL was developed in Python 3.6.
    - Update your local apt cache data: `apt-get update`
    - Install Python 3.x: `apt-get install python3 python3-pip`
- Create the directories and service account for PyTerraBackTYL:
    - Create the non-privileged user that will run the PyTerraBackTYL service: `adduser tfbackendsvc` (this also creates a directory for the user in `/home` which you will likely need.)
    - Create the directory the PyTerrBackTYL service will run from: `mkdir /opt/pyterrabacktyl`
    - Set directory ownership: `chown -R tfbackendsvc /opt/pyterrabacktyl`
- Install PyTerraBackTYL and dependencies:
    - Clone the PyTerraBackTYL repository:
      - `cd /opt/pyterrabacktyl`
      - `su tfbackendsvc`
      - `git clone https://github.com/dev-dull/PyTerraBackTyl.git`
    - Install the required Python Libraries: 
      - _Note_: Depending on your OS and Python installation method, the `pip3` command may be something like, `pip3.6`.
      - _Note_: Omit the `--user` flag and run as root if you want these libraries to be accessible to all users on the system.
      - `pip3 install flask gitpython pyyaml --user`

#### Configuring PyTerraBackTYL:
The contents of the `config.yaml` configuration file will largely depend on which backend module you choose to
to use with PyTerraBackTYL. Below are the configuration items for core PyTerraBackTYL service:

- `BACKEND_SERVICE_IP: '127.0.0.1'`
  - The IP the service should listen for requests on. If you are unsure what to use here, set `0.0.0.0`
- `BACKEND_SERVICE_PORT: 2442`
  - The port number the service should listen on.
- `BACKEND_PLUGINS_PATH: 'backends'`
  - The directory where PyTerraBackTYL can find the Backend plugins.
  - The value shown here means the `backends` subdirectory where PyTerraBackTYL is installed.
- `BACKEND_CLASS: 'git_backend.GitBackend'`
  - The file and class name of the PyTerraBackTYL plugin to use; Python will look in a file called `git_backend.py`
  for the class `GitBackend`
- `LOG_LEVEL: 'INFO'` 
  - The amount of info to log. Valid values are: INFO, DEBUG, WARNING, ERROR
  - If an invalid value is specified, PyTerraBackTYL will default to INFO.
  
#### Setup and Configure the GitBackend module:
- Create SSH keypair:
  - SSH to the host running the PyTerraBackTYL service and become the user running the service (e.g. `su tfbackendsvc`) 
  - Check if a keypair already exists: `ls -lah ~/.ssh`
  - Generate a keypair if needed: `ssh-keygen -t rsa` leave all prompts empty by pressing enter until the command completes.
- Set the git global config for the tfbackendsvc user:
  - `git config --global user.email "you@example.com"`
  - `git config --global user.name "Your Name"`
- Create a new Git repository.
  - **WARNING**: Make this repository private as `terraform.tfstate` files can contain sensitive information about your infrastructure.
  - This process will vary between various Git services (GitHub, GitLab, et. al.)
- Add the public key to grant permissions to the Git repository
  - Copy and paste the contents of `~/.ssh/id_rsa.pub` to grant permissions for the tfbackendsvc user to make changes to the newly created repository. This process will vary between various Git services.
  - Do an initial clone, add, commit, and push to the repository as the tfbackendsvc user to verify everything is working as expected.
- Modify the `config.yaml` configuration file.
  - Optional settings:
    - `GIT_WORKING_PATH: null` 
      - When omitted or `null`, GitBackend will use the default temporary directory of the operating system.
      - If you set a value here, make sure the directory exists and that you have set the correct ownership/permissions.
  - Required settings:
    - `GIT_REPOSITORY: 'git@github.com:dev-dull/backend_test.git'`
      - The newly created Git repository.
      - Note: HTTP/HTTPS repositories are not currently supported.
    - `GIT_DEFAULT_CLONE_BRANCH: 'origin/master'`
      - If you're unsure, just use the default here.
    - `GIT_COMMIT_MESSAGE_FORMAT: '{Who}, {Operation} - {ID}'`
      - The string format to use when making commits to the repository
      - valid values are:
        - ID: An ID created by Terraform.
        - Operation: The Terraform operation being carried out (plan, apply, etc.)
        - Info: (TODO: check terraform documentation) 
        - Who: The username and hostname who initiated the terraform command.
        - Version: The version of Terraform that was used.
        - Created: Timestamp of when the terraform command ws run.
        - Path: (TODO: check terraform documentation)
    - `GIT_STATE_CHANGE_LOG_SCROLLBACK: 300`
      - The maximum number of rows to keep in log file commited alongside terraform.tfstate.
    - `GIT_STATE_CHANGE_LOG_FILENAME: 'state_change.log'`
      - The name of the log file to be commited alongside terraform.tfstate
    - `GIT_STATE_CHANGE_LOG_FORMAT: '{Created} - {Operation}: {Who} {ID}'`
      - The details to record in the log file commited alongside terraform.tfstate
      - See the list of values for the commit message for valid values here.
  - Start and test the PyTerraBackTYL service
    - `su tfbackendsvc`
    - `cd /opt/pyterrabacktyl/PyTerraBackTyl`
    - `nohup python3 pyterrabacktyl.py 2>&1 > pyterrabacktyl.log &`
    - `curl http://localhost:2442/state`
    
#### Configure your Terraform project to use the PyTerraBackTYL Service:
In your project, configure the HTTP backend service:
```
terraform {
  backend "http" {
    address = "http://localhost:2442/?env=DEVTEST"
    lock_address = "http://localhost:2442/lock?env=DEVTEST"
    unlock_address = "http://localhost:2442/unlock?env=DEVTEST"
  }
}
```

Change 'localhost' to the hostname or IP of where the PyTerraBackTYL service is running.

***WARNING***: The `?env=YOURVALUE` is how PyTerraBackTYL tracks states across multiple environments (e.g. production, test, QA, etc.). Be sure that you are always setting the value of this parameter to accurately to reflect the environment you are making changes to. You likely already have a variable in your terraform files that reflects the environment. Use this value here.

## But I don't want to use Git as a backend:
That's fine. Subclass `abc_tylstore.TYLStore`, implement the required functions, drop your module into the `backends` directory, update your `config.yaml` to point at your new module, and try not to break production in the process of testing.
