.. _aes_backend:

.. role:: bash(code)
  :language: bash

.. role:: yaml(code)
  :language: yaml

Configuring the AES Encryption Backend
======================================
The AES backend plugin encrypts Terraform locking and state information with 256bit CBC mode AES encryption, and the persists the result to disk.

Modify :bash:`config.yaml` and set the following items to the desired values.

- :yaml:`AES_DATA_PATH: '/opt/pyterrabacktyl/data'`
    - The directory to save the encrypted data.
    - The user running the PyTerraBackTYL service *must* have read/write access to this directory.
    - Do NOT set this value to a temporary director (such as /tmp)
- :yaml:`AES_TFSTATE_FILENAME: '_aes_tfstate.bin'`
    - The file name to use for encrypted state files.
    - _Note:_ The name of the environment will be prepended to this file name (e.g. if 'QA' is set as the environment name, the file 'QA_aes_tfstate.bin' will be created).
- :yaml:`AES_TFLOCK_FILENAME: '_LOCKED.bin'`
    - The file name to use for encrypted lock files.
    - _Note:_ The name of the environment will be prepended to this file name (e.g. if 'QA' is set as the environment name, the file 'QA_LOCKED.bin' will be created).
- :yaml:`AES_SECRET_KEY: 'This value will be used to encrypt data'`
    - The value to use to encrypt the data with.
    - This value should be 32 characters long, but the plugin will adjust if the value is too long or too short.
    - It is recommended that you :bash:`chmod 600 config.yaml` to avoid leaking this value.
    - By using double quotes (e.g. :yaml:`"secret string with \a system bell"`) you can use standard escape sequences to include characters like tab, new line, etc.
    - **WARNING**: Once this value is set, changing it will make it impossible to decrypt the data that has already been persisted to disk.

Full example configuration for the PyShelveBackend module:
----------------------------------------------------------
.. code:: yaml

  ##
  ##  aes_backend.AESBackend configuration
  ##

  AES_DATA_PATH: '/opt/pyterrabacktyl/data'  # Path where the encrypted files will be kept.
  AES_TFSTATE_FILENAME: '_aes_tfstate.bin'  # The name of the state file with the environment prepended.
  AES_TFLOCK_FILENAME: '_LOCKED.bin'  # The name of the lock file with the environment prepended.
  AES_SECRET_KEY: 'This value will be used to encrypt data'  # String value used to encrypt and decrypt data. If you change this, you will break things.
