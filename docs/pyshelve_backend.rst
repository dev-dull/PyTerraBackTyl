.. _pyshelve_backend:

.. role:: bash(code)
  :language: bash

.. role:: yaml(code)
  :language: yaml

Configuring the (defualt) PyShelve Backend
==========================================
The PyShelve plugin stores Terraform locking and state data as a Python object to disk. If this is your first time configuring PyTerraBackTYL, it is recommended that you start with this class to validate service configuration. Once you've validated PyTerraBackTYL is working as expected, you can change your `BACKEND_CLASS` setting to the module you plan on using for handling Terraform state.

Modify :bash:`config.yaml` and set the following items to the desired values.

- :yaml:`PYSHELVE_DATA_PATH: '/opt/pyterrabacktyl/data'`
    - The directory to save Python 'shelve' files that contain state.
    - The user running the PyTerraBackTYL service *must* have read/write access to this directory.
    - Do NOT set this value to a temporary director (such as /tmp)
- :yaml:`PYSHELVE_DB_FILE_NAME: '_terraform_state'`
    - The file name to use for Python 'shelve' oblects.
    - _Note:_ The name of the environment will be prepended to this file name (e.g. if 'QA' is set as the environment name, the file 'QA_terraform_state' will be created).

Full example configuration for the PyShelveBackend module:
----------------------------------------------------------
.. code:: yaml

  ##
  ##  pyshelve_backend.PyShelveBackend configuration
  ##

  # The path to where the python shelf objects should be saved (no trailing slash).
  PYSHELVE_DATA_PATH: '/opt/pyterrabacktyl/data'

  # The filename for the tfstate shelf objects -- the environment name will be prepended
  # e.g. for environment TEST, file name will be TEST_terraform_state
  PYSHELVE_DB_FILE_NAME: '_terraform_state'
