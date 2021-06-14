# PyTerraBackTYL
![PyTerraBackTYL logo](http://www.devdull.lol/pyterrabacktyl/pyterrabacktyl_logo_v2.png)

## About:
PyTerraBackTYL is a generic HTTP/REST backend that uses plugins for managing your Terraform state and locking in whatever way you see fit. By default, PyTerraBackTYL comes with plugins to manage locking and state using Git, or using simple 'shelve' objects to persist to disk. Additionally, non-persistent plugins can be used to automate tasks when a user has issued a `terraform` command, such as automatically adding the new hosts into monitoring, or pushing notifications to Slack like in the provided example.

## Setup:
For detailed setup instructions, see the [documentation on readthedocs.io](https://pyterrabacktyl.readthedocs.io/en/latest/).

## Docker:
Visit [PyTerraBackTYL Docker Hub page](https://hub.docker.com/r/devdull/pyterrabacktyl) to get up and running quickly. By default, the container starts up using the PyShelveBackend module, but contains all package requirements for the GitBackend and the AESBackend.

## Quickstart:
### Requirements:
- PyTerraBackTYL was developed using Python 3.6 and is subsequently recommended, but 3.4 and 3.5 have been tested and known to work well.
  - flask
  - pyyaml
  - jsonpath

### Installation instructions:
#### Install PyTerraBackTYL:
- SSH to the host you intend to run the PyTerraBackTYL service on.
  - e.g. `ssh user@linuxhost`
- Check if `python3` is installed.
  - e.g. `whereis python3`
- Install Python 3.x if needed
  - RedHat/CentOS ([detailed instructions](https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-local-programming-environment-on-centos-7)):
    - Install yum utils: `yum install yum-utils`
    - Install libs/dependencies: `yum groupinstall development`
    - Install the Yum Repo with Python 3.x: `yum -y install https://centos7.iuscommunity.org/ius-release.rpm`
    - Install Python 3.x: `yum -y install python36u python36u-pip`
  - Debian/Ubuntu:
    - Note: This currently installs Python 3.5, PyTerraBackTYL was developed in Python 3.6.
    - Update your local apt cache data: `apt-get update`
    - Install Python 3.x: `apt-get install python3 python3-pip`
- Create the directories and service account for PyTerraBackTYL:
    - Create the non-privileged user that will run the PyTerraBackTYL service: `adduser tfbackendsvc` (this also creates a directory for the user in `/home` which you will need.)
    - Create the directory the PyTerrBackTYL service will run from: `mkdir /opt/pyterrabacktyl`
    - Create the directory the service will store Terraform states in: `mkdir /opt/pyterrabacktyl/data`
    - Set directory ownership: `chown -R tfbackendsvc /opt/pyterrabacktyl`
- Install PyTerraBackTYL and dependencies:
    - Clone the PyTerraBackTYL repository:
      - `cd /opt/pyterrabacktyl`
      - `su tfbackendsvc`
      - `git clone https://github.com/dev-dull/PyTerraBackTyl.git`
    - Install the required Python Libraries:
      - _Note_: Depending on your OS and Python installation method, the `pip3` command may be something like, `pip3.6`.
      - _Note_: Omit the `--user` flag and run as root if you want these libraries to be accessible to all users on the system.
      - `pip3 install setuptools --user` requried to install Flask.
      - `pip3 install flask pyyaml jsonpath --user`

#### Configuring PyTerraBackTYL:
The contents of the `config.yaml` configuration file will largely depend on which backend module you choose to
to use with PyTerraBackTYL. Below are the configuration items for core PyTerraBackTYL service:

Modify `config.yaml` and set the following items to the desired values.
- `BACKEND_SERVICE_IP: '127.0.0.1'`
  - The IP the service should listen for requests on. If you are unsure what to use here, set `0.0.0.0`
- `BACKEND_SERVICE_PORT: 2442`
  - The port number the service should listen on.
- `BACKEND_PLUGINS_PATH: 'backends'`
  - The directory where PyTerraBackTYL can find the Backend plugins.
  - The value shown here means the `backends` subdirectory where PyTerraBackTYL is installed.
- `BACKEND_CLASS: 'pyshelve_backend.PyShelveBackend'`
  - The file and class name of the PyTerraBackTYL plugin to use; Python will look in a file called `pyshelve_backend.py`
  for the class `PyShelveBackend`
- `POST_PROCESS_CLASSES: ['slack_notify_post_processor.SlackNotifyPostProcessor']`
  - A list where each item contains a file and class name of a PyTerraBackTYL nonpersistent plugin to use; Python will look in a file called `slack_notify_post_processor.py`
  for the class `SlackNotifyPostProcessor`. Set this to an empty list (i.e. `[]`) if you do not wish to use any post-processors.
- `LOG_LEVEL: 'INFO'`
  - The amount of information to log. Valid values are: INFO, DEBUG, WARNING, ERROR
  - If an invalid value is specified, PyTerraBackTYL will default to INFO.
- `USE_SSL: false`
  - Disabled by default, this specifies if the service should use SSL (HTTPS) or not (HTTP).
  - A Bash script can be found in the `ssl` subdirectory which will generate these keys.
- `SSL_PUBLIC_KEY: 'ssl/public.key'`
  - The path and filename where the SSL public key can be found.
  - The value shown here means the `ssl/` subdirectory where PyTerraBackTYL is installed.
- `SSL_PRIVATE_KEY: 'ssl/private.key'`
  - The path and filename where the SSL private key can be found.
  - The value shown here means the `ssl/` subdirectory where PyTerraBackTYL is installed.
- `HELPER_HOSTNAME_QUERY_MAP:`
  - Generally, this should not need to be changed.
  - Contains key:value pairs where the key is the name of a Terraform provider (an exact match for what is found in a Terraform state file) and the value is a JSONPath that will return the hostnames found in a Terraform state file for that provider type.
  - This configuration is used by the `TYLHelpers.get_hostnames_from_tfstate` function (`from abc_tylstore import TYLHelpers`)

##### Full example configuration for the PyTerraBackTYL service.  
```yaml
## IP and ports to listen on. Defaults shown.
BACKEND_SERVICE_IP: '0.0.0.0'
BACKEND_SERVICE_PORT: 2442

BACKEND_PLUGINS_PATH: 'backends'
BACKEND_CLASS: 'pyshelve_backend.PyShelveBackend'
POST_PROCESS_CLASSES:
  - 'slack_notify_post_processor.SlackNotifyPostProcessor'

LOG_LEVEL: 'DEBUG' # INFO, DEBUG, WARNING, ERROR

# openssl req -x509 -nodes -days 3650 -newkey rsa:4096 -keyout private.key -out public.key -passout "pass:"
USE_SSL: false  # Disabled by default -- generate SSL key pair then set this to 'true'
SSL_PUBLIC_KEY: 'ssl/public.key'  # The path and filename of the public SSL key -- 'ssl/' is a subdirectory where PyTerraBackTYL is installed.
SSL_PRIVATE_KEY: 'ssl/private.key'  # The path and file name of the private SSL key.

# Key:Value pairs where the key matches a Terraform provider, and key is a jsonPath to fetch hostnames from the terraform state
HELPER_HOSTNAME_QUERY_MAP:
  digitalocean_droplet: 'modules[*].resources.*.primary.attributes.name'
  vsphere_virtual_machine: '$.modules[*].resources.[?(@.type == "vsphere_virtual_machine")].primary[?(@.memory != 0)].name'
```

#### Configuring the PyTerraBackTYL backend plugin:
##### Option 1: Configuring the PyShelveBackend (default backend module):
If this is your first time configuring PyTerraBackTYL, it is recommended that you start with this class to validate service configuration. Once you've validated PyTerraBackTYL is working as expected, you can change your `BACKEND_CLASS` setting to the module you plan on using for handling Terraform state.

Modify `config.yaml` and set the following items to the desired values.
- `PYSHELVE_DATA_PATH: '/opt/pyterrabacktyl/data'`
  - The directory to save Python 'shelve' files that contain state.
  - The user running the PyTerraBackTYL service *must* have read/write access to this directory.
  - Do NOT set this value to a temporary director (such as /tmp)
- `PYSHELVE_DB_FILE_NAME: '_terraform_state'`
  - The file name to use for Python 'shelve' oblects.
  - _Note:_ The name of the environment will be prepended to this file name (e.g. if 'QA' is set as the environment name, the file 'QA_terraform_state' will be created).

###### Full example configuration for the PyShelveBackend module:
```yaml
##
##  pyshelve_backend.PyShelveBackend configuration
##

# The path to where the python shelf objects should be saved (no trailing slash).
PYSHELVE_DATA_PATH: '/opt/pyterrabacktyl/data'

# The filename for the tfstate shelf objects -- the environment name will be prepended
# e.g. for environment TEST, file name will be TEST_terraform_state
PYSHELVE_DB_FILE_NAME: '_terraform_state'
```

##### Option 2: Setup and Configure the GitBackend module:
- SSH to the host running the PyTerraBackTYL service and become the user running the service (e.g. `su tfbackendsvc`)
- Install GitPython: `pip3 install GitPython --user`
- Create SSH keypair:
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

###### Full example configuration for GitBackend
```yaml
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
```

##### Option 3: Create your own backend module:
PyTerraBackTYL was developed with the expectation that you're looking at this project because you would like to manage your Terraform state file in a method not already handled by one of the standard backends. For this reason, PyTerraBackTYL allows you to implement your own backend handler. The following is a brief outline on how to implement a custom backend module. Refer to the [PyShelveBacked](https://github.com/dev-dull/PyTerraBackTyl/blob/master/backends/pyshelve_backend.py) class for an example.

---

***Note:*** Except in very rare cases, you should not do any exception handling. Any failures should be allowed to be raised so the exception (HTTP status code 500) is sent to Terraform. This prevents Terraform from continuing and lets the user know the action did not work as expected.)

---

Import `TYLPersistent` and define your subclass:
```python
from abc_tylstore import TYLPersistent
class MyPersistentBackend(TYLPersistent):...
```

Implement the following functions in your class:
- `__init__(self, environment, constants, **kwargs):`
  - `environment` every environment will get a separate instance of your class and as a result, this value should be treated as a constant. Use this value to keep environment states isolated from each other. For example, if you are saving your Terraform states into plain text files, you'd likely want your file name to be something like `<environment>_terraform.tfstate`
  - `constants` a python class containing constant values. These values are partly populated by `config.yaml` as key:value pairs. For example, if you set `MY_BACKEND_FOO: 'Hello, World!'` in `config.yaml`, you can access the string value with `constants.MY_BACKEND_FOO`. This allows you to configure your backend module without the need of a separate configuration file.
  - `**kwargs` It is recommended to add this to help ensure forward compatibility of your module with future versions of PyTerraBackTYL.
- `def set_locked(self, state_obj, **kwargs):`
  - `state_obj` Unpacked JSON (`dict`) with the specifics on who is putting a lock on the environment.
  - `**kwargs` includes `raw` which contains the original JSON string (`str`) value.
  - **RETURNS**: value that evaluates to `True` on a successful lock; value that evaluates to `False` when someone else is already holding the lock.
- `def set_unlocked(self, state_obj, **kwargs):`
  - `state_obj` Unpacked JSON (`dict`) with the specifics on who is unlocking the environment. The `ID` value should match the one provided when lock was created. However, when a user issues a `terraform force-unlock <ID value>` command, the ID is not currently being passed to the backend. Validating the ID in this function will make forcing an unlock impossible until HashiCorp addresses this deficiency.
  - `**kwargs` includes `raw` which contains the original JSON string (`str`) value.
  - **RETURNS**: value that evaluates to `True` on a successful unlock; value that evaluates to `False` when the environment is NOT still locked (logs warning message).
- `def get_lock_state(self):`
  - **RETURNS**: The string (`str`) or JSON compatible object of the lock (the value received in `set_locked()`). Return and empty string when no lock is held.
- `def store_tfstate(self, tfstate_obj, **kwargs):`
  - `tfstate_obj` Unpacked JSON (`dict`) which specifies the current terraform state (`terraform.tfstate`)
  - `**kwargs` includes `raw` which contains the original JSON string (`str`) value.
  - No return value. Return `None` if needed.
- `def get_tfstate(self):`
  - **RETURNS**: The string (`str`) or JSON compatible object of the Terraform state (the value received in `store_tfstate()`).
- `def backend_status(self):` _OPTIONAL_
  - **RETURNS**: A JSON compatible object containing health and status information about the backend. This is a good place to report where data is being stored and lock state for the environment.

#### Start and test the PyTerraBackTYL service
- `su tfbackendsvc`
- `cd /opt/pyterrabacktyl/PyTerraBackTyl`
- `./start.sh` Modify this script to change the location of log file if needed.
- `curl -s http://localhost:2442/state` Check the current state of the backend. When first started, output will appear similar to the below.

```json
{
  "backend_module": "pyshelve_backend.PyShelveBackend",
  "post_processor_modules": [
    "zenoss_post_processor.ZenossPostProcessor",
    "slack_notify_post_processor.SlackNotifyPostProcessor"
  ],
  "environments": []
}
```

#### Configure your Terraform project to use the PyTerraBackTYL Service:
In your project, configure the HTTP backend service:
```hcl
terraform {
  backend "http" {
    address = "http://localhost:2442/?env=DEVTEST"
    lock_address = "http://localhost:2442/lock?env=DEVTEST"
    unlock_address = "http://localhost:2442/unlock?env=DEVTEST"
    skip_cert_verification = "true"
  }
}
```

Remember to change 'localhost' to the hostname or IP of where the PyTerraBackTYL service is running, and to change `http` to `https` if you are using SSL.

---

***WARNING***: The `?env=YOURVALUE` is how PyTerraBackTYL tracks states across multiple environments (e.g. production, test, QA, etc.). Be sure that you are always setting the value of this parameter to accurately to reflect the environment you are making changes to.

---

### *Optional:* Create a non-persistent, 'post-processor' backend:
Similarly to how custom backend modules are managed, you can also create a `TYLNonpersistent` backend. These are optional backends that don't store any locking or state data, but rather allow you the opportunity to parse the Terraform lock and state files to perform other actions. Examples of tasks you may want to perform with a non-persistent backed include adding new hosts to monitoring, generating a chat notification that a user has performed an action, generating a report email containing a list of new hostnames, etc. These non-persistent backends should be kept in the same directory as the persistent backends (e.g. the `backends` directory). You can reference the [SlackNotifyPostProcessor](https://github.com/dev-dull/PyTerraBackTyl/blob/master/backends/slack_notify_post_processor.py) as an example.

---

***Note:*** All exceptions raised by non-persistent backends are ignored as they cannot be allowed to interfere with the functionality of the *persistent* backend which is handling state and locking.

---

Example `config.yaml` configuration for multiple non-persistent backends:
```yaml
POST_PROCESS_CLASSES:
  - 'zenoss_post_processor.ZenossPostProcessor'
  - 'slack_notify_post_processor.SlackNotifyPostProcessor'
```

Import `TYLNonpersistent` and define your subclass:
```python
from abc_tylstore import TYLNonpersistent
class MyNonpersistentBackend(TYLNonpersistent):...
```

Implement the following functions in your class:
- `__init__(self, environment, constants, **kwargs):`
  - `environment` every environment will get a separate instance of your class and as a result, this value should be treated as a constant.
  - `constants` a python class containing constant values. These values are partly populated by `config.yaml` as key:value pairs. For example, if you set `MY_POST_PROCESSOR_FOO: 'Hello, World!'` in `config.yaml`, you can access the string value with `constants.MY_POST_PROCESSOR_FOO`. This allows you to configure your backend module without the need of a separate configuration file.
  - `**kwargs` It is recommended to add this to help ensure forward compatibility of your module with future versions of PyTerraBackTYL.
- `def on_locked(self, state_obj, **kwargs):`
  - `state_obj` Unpacked JSON (`dict`) with the specifics on who is putting a lock on the environment.
  - `**kwargs` includes `raw` which contains the original JSON string (`str`) value.
  - No return value. Return `None` if needed.
- `def on_unlocked(self, state_obj, **kwargs):`
  - `state_obj` Unpacked JSON (`dict`) with the specifics on who is unlocking the environment.
  - `**kwargs` includes `raw` which contains the original JSON string (`str`) value.
  - No return value. Return `None` if needed.
- `def process_tfstate(self, tfstate_obj, **kwargs):`
  - `tfstate_obj` Unpacked JSON (`dict`) which specifies the current terraform state (`terraform.tfstate`)
  - `**kwargs` includes `raw` which contains the original JSON string (`str`) value.
  - No return value. Return `None` if needed.
- `def post_processor_status(self):` _OPTIONAL_
  - **RETURNS**: A JSON compatible object containing health and status information about the backend. This is a good place to report where data is being stored.
  
### Troubleshooting:
- As always, check the log. If you haven't modified the default start script, a new subdirectory called `logs` will be created in the same location as the script.
- Check what information is found in the `/state` endpoint. You can monitor state changes with the command `watch -d "curl -s http://localhost:2442/state"`.

## Thanks and Acknowledgements:
PyTerraBackTYL art and logos are based on the creative works of Matthew Green. Show your support and visit his website [TetraVariations](https://tetravariations.wordpress.com/), or purchase something rad from his [Etsy store](https://www.etsy.com/shop/TetraVariations?ref=l2-shopheader-name)! 
