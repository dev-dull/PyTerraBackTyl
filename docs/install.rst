.. _install:

.. role:: bash(code)
  :language: bash

.. role:: yaml(code)
  :language: yaml

PyTerraBackTYL Installation
===========================
Install PyTerraBackTYL:
-----------------------
- SSH to the host you intend to run the PyTerraBackTYL service on.
    - e.g. :bash:`ssh user@linuxhost`
- Check if :bash:`python3` is installed.
    - e.g. :bash:`whereis python3`
- Install Python 3.x if needed
    - RedHat/CentOS (`detailed instructions`_):
        - Install yum utils: :bash:`yum install yum-utils`
        - Install libs/dependencies: :bash:`yum groupinstall development`
        - Install the Yum Repo with Python 3.x: :bash:`yum -y install https://centos7.iuscommunity.org/ius-release.rpm`
        - Install Python 3.x: :bash:`yum -y install python36u python36u-pip`
    - Debian/Ubuntu:
        - Note: This currently installs Python 3.5, PyTerraBackTYL was developed in Python 3.6.
        - Update your local apt cache data: `apt-get update`
        - Install Python 3.x: :bash:`apt-get install python3 python3-pip`
    - Create the directories and service account for PyTerraBackTYL:
        - Create the non-privileged user that will run the PyTerraBackTYL service: :bash:`adduser tfbackendsvc` (this also creates a directory for the user in `/home` which you will need.)
        - Create the directory the PyTerrBackTYL service will run from: :bash:`mkdir /opt/pyterrabacktyl`
        - Create the directory the service will store Terraform states in: :bash:`mkdir /opt/pyterrabacktyl/data`
        - Set directory ownership: :bash:`chown -R tfbackendsvc /opt/pyterrabacktyl`
    - Install PyTerraBackTYL and dependencies:
        - Clone the PyTerraBackTYL repository:
            - :bash:`cd /opt/pyterrabacktyl`
            - :bash:`su tfbackendsvc`
            - :bash:`git clone https://github.com/dev-dull/PyTerraBackTyl.git`
        - Install the required Python Libraries:
            - _Note_: Depending on your OS and Python installation method, the :bash:`pip3` command may be something like, :bash:`pip3.6`.
            - _Note_: Omit the `--user` flag and run as root if you want these libraries to be accessible to all users on the system.
            - :bash:`pip3 install setuptools --user` requried to install Flask.
            - :bash:`pip3 install flask pyyaml jsonpath --user`

.. _detailed instructions: https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-local-programming-environment-on-centos-7

Configuring PyTerraBackTYL:
---------------------------
The contents of the :bash:`config.yaml` configuration file will largely depend on which backend module you choose to
to use with PyTerraBackTYL. Below are the configuration items for core PyTerraBackTYL service:

Modify :bash:`config.yaml` and set the following items to the desired values.

- :yaml:`BACKEND_SERVICE_IP: '127.0.0.1'`
    - The IP the service should listen for requests on. If you are unsure what to use here, set `0.0.0.0`
- :yaml:`BACKEND_SERVICE_PORT: 2442`
    - The port number the service should listen on.
- :yaml:`BACKEND_PLUGINS_PATH: 'backends'`
    - The directory where PyTerraBackTYL can find the Backend plugins.
    - The value shown here means the `backends` subdirectory where PyTerraBackTYL is installed.
- :yaml:`BACKEND_CLASS: 'pyshelve_backend.PyShelveBackend'`
    - The file and class name of the PyTerraBackTYL plugin to use; Python will look in a file called `pyshelve_backend.py` for the class `PyShelveBackend`
- :yaml:`POST_PROCESS_CLASSES: ['slack_notify_post_processor.SlackNotifyPostProcessor']`
    - A list where each item contains a file and class name of a PyTerraBackTYL nonpersistent plugin to use; Python will look in a file called `slack_notify_post_processor.py` for the class `SlackNotifyPostProcessor`. Set this to an empty list (i.e. `[]`) if you do not wish to use any post-processors.
- :yaml:`LOG_LEVEL: 'INFO'`
    - The amount of information to log. Valid values are: INFO, DEBUG, WARNING, ERROR
    - If an invalid value is specified, PyTerraBackTYL will default to INFO.
- :yaml:`USE_SSL: false`
    - Disabled by default, this specifies if the service should use SSL (HTTPS) or not (HTTP).
    - A Bash script can be found in the :bash:`ssl` subdirectory which will generate these keys.
- :yaml:`SSL_PUBLIC_KEY: 'ssl/public.key'`
    - The path and filename where the SSL public key can be found.
    - The value shown here means the `ssl/` subdirectory where PyTerraBackTYL is installed.
- :yaml:`SSL_PRIVATE_KEY: 'ssl/private.key'`
    - The path and filename where the SSL private key can be found.
    - The value shown here means the `ssl/` subdirectory where PyTerraBackTYL is installed.
- :yaml:`HELPER_HOSTNAME_QUERY_MAP:`
    - Generally, this should not need to be changed.
    - Contains key:value pairs where the key is the name of a Terraform provider (an exact match for what is found in a Terraform state file) and the value is a JSONPath that will return the hostnames found in a Terraform state file for that provider type.
    - This configuration is used by the `TYLHelpers.get_hostnames_from_tfstate` function (`from abc_tylstore import TYLHelpers`)

Full example configuration for the PyTerraBackTYL service
---------------------------------------------------------
.. code:: yaml

  ## IP and ports to listen on. Defaults shown.
  BACKEND_SERVICE_IP: '0.0.0.0'
  BACKEND_SERVICE_PORT: 2442

  BACKEND_PLUGINS_PATH: 'backends'
  BACKEND_CLASS: 'pyshelve_backend.PyShelveBackend'
  POST_PROCESS_CLASSES: []  # Remember to remove "[]" before uncommenting the below line.
  #  - 'slack_notify_post_processor.SlackNotifyPostProcessor'

  LOG_LEVEL: 'DEBUG' # INFO, DEBUG, WARNING, ERROR

  # openssl req -x509 -nodes -days 3650 -newkey rsa:4096 -keyout private.key -out public.key -passout "pass:"
  USE_SSL: false  # Disabled by default -- generate SSL key pair then set this to 'true'
  SSL_PUBLIC_KEY: 'ssl/public.key'  # The path and filename of the public SSL key -- 'ssl/' is a subdirectory where PyTerraBackTYL is installed.
  SSL_PRIVATE_KEY: 'ssl/private.key'  # The path and file name of the private SSL key.

  # Key:Value pairs where the key matches a Terraform provider, and key is a jsonPath to fetch hostnames from the terraform state
  HELPER_HOSTNAME_QUERY_MAP:
    digitalocean_droplet: 'modules[*].resources.*.primary.attributes.name'
    vsphere_virtual_machine: '$.modules[*].resources.[?(@.type == "vsphere_virtual_machine")].primary[?(@.memory != 0)].name'
