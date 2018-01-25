.. _git_backend:

.. role:: bash(code)
  :language: bash

.. role:: yaml(code)
  :language: yaml

Configuring the Git Backend
===========================
The Git backend plugin keeps Terraform locking and state information in the configured Git repository.

.. caution::

  Terraform state files may sometimes contain sensitive information such as usernames, passwords, and authentication tokens like ssh keys. For this reason, you should take care that the Git repository you use is restricted to only the individuals who need access to the information. The repository should always be protected and ideally, hosted on an internal network.

- SSH to the host running the PyTerraBackTYL service and become the user running the service (e.g. `su tfbackendsvc`)
- Install GitPython: :bash:`pip3 install GitPython --user`
- Create SSH keypair:
    - Check if a keypair already exists: :bash:`ls -lah ~/.ssh`
    - Generate a keypair if needed: :bash:`ssh-keygen -t rsa` leave all prompts empty by pressing enter until the command completes.
- Set the git global config for the tfbackendsvc user:
    - :bash:`git config --global user.email "you@example.com"`
    - :bash:`git config --global user.name "Your Name"`
- Create a new Git repository.
    - **WARNING**: Make this repository private as `terraform.tfstate` files can contain sensitive information about your infrastructure.
    - This process will vary between various Git services (GitHub, GitLab, et. al.)
- Add the public key to grant permissions to the Git repository
    - Copy and paste the contents of :bash:`~/.ssh/id_rsa.pub` to grant permissions for the tfbackendsvc user to make changes to the newly created repository. This process will vary between various Git services.
    - Do an initial clone, add, commit, and push to the repository as the tfbackendsvc user. This will prompt you to accept the SSH key from the git server which is required for the backend plugin to work.
- Modify the :bash:`config.yaml` configuration file.
    - Optional settings:
        - :yaml:`GIT_WORKING_PATH: null`
            - When omitted or `null`, GitBackend will use the default temporary directory of the operating system.
            - If you set a value here, make sure the directory exists and that you have set the correct ownership/permissions.
    - Required settings:
        - :yaml:`GIT_REPOSITORY: 'git@github.com:dev-dull/backend_test.git'`
            - The newly created Git repository.
            - Note: HTTP/HTTPS repositories are not currently supported.
        - :yaml:`GIT_DEFAULT_CLONE_BRANCH: 'origin/master'`
            - If you're unsure, just use the default here.
        - :yaml:`GIT_COMMIT_MESSAGE_FORMAT: '{Who}, {Operation} - {ID}'`
            - The string format to use when making commits to the repository
            - valid values are:
                - ID: An ID created by Terraform.
                - Operation: The Terraform operation being carried out (plan, apply, etc.)
                - Info: (TODO: check terraform documentation)
                - Who: The username and hostname who initiated the terraform command.
                - Version: The version of Terraform that was used.
                - Created: Timestamp of when the terraform command ws run.
                - Path: (TODO: check terraform documentation)
        - :yaml:`GIT_STATE_CHANGE_LOG_SCROLLBACK: 300`
            - The maximum number of rows to keep in log file commited alongside terraform.tfstate.
        - :yaml:`GIT_STATE_CHANGE_LOG_FILENAME: 'state_change.log'`
            - The name of the log file to be commited alongside terraform.tfstate
        - :yaml:`GIT_STATE_CHANGE_LOG_FORMAT: '{Created} - {Operation}: {Who} {ID}'`
            - The details to record in the log file commited alongside terraform.tfstate
            - See the list of values for the commit message for valid values here.

Full example configuration for GitBackend
-----------------------------------------
.. code:: yaml

  ##
  ##  git_backend.GitBackend configuration
  ##

  ## --- Optional settings: ---
  GIT_WORKING_PATH: null  # Let the app create one in the temp directory of the OS.

  ## --- REQUIRED settings! ---
  # The SSH repo to use to store tfstate, lock status, and logs.
  GIT_REPOSITORY: 'git@github.com:dev-dull/backend_test.git'  # No HTTP/S yet.

  # The branch to clone when creating a new environment with Terraform.
  GIT_DEFAULT_CLONE_BRANCH: 'origin/master'

  # The format to use for commit messages. Options are case sensitive.
  # Valid values: ID, Operation, Info, Who, Version, Created, Path
  GIT_COMMIT_MESSAGE_FORMAT: '{Who}, {Operation} - {ID}'

  # Maximum number of log messages to keep in the GIT_STATE_CHANGE_LOG_FILENAME file.
  GIT_STATE_CHANGE_LOG_SCROLLBACK: 300

  # Name of the log file to commit to record locks/unlocks
  GIT_STATE_CHANGE_LOG_FILENAME: 'state_change.log'

  # The format to use for logging messages. Options are case sensitive.
  # Valid values: ID, Operation, Info, Who, Version, Created, Path
  GIT_STATE_CHANGE_LOG_FORMAT: '{Created} - {Operation}: {Who} {ID}'
