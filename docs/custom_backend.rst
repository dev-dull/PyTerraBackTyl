.. _custom_backend:

.. role:: bash(code)
  :language: bash

.. role:: python(code)
  :language: python

.. role:: yaml(code)
  :language: yaml

Developing a custom persistent backend
======================================
PyTerraBackTYL was developed with the expectation that you're looking at this project because you would like to manage your Terraform state file in a method not already handled by one of the standard backends. For this reason, PyTerraBackTYL allows you to implement your own backend handler. The following is a brief outline on how to implement a custom backend module. Refer to the TemplateBacked_ class for an example. Note that **the template is only an example and does not persist any data to disk**. Subsequently, any information that Terraform has sent to the PyTerraBackTYL backend will be lost when the service is restarted.

.. _TemplateBacked: https://github.com/dev-dull/PyTerraBackTyl/blob/master/backends/TEMPLATE_backend.py

.. note::

  Except in very rare cases, you should not do any exception handling. Any failures should be allowed to be raised so the exception (HTTP status code 500) is sent to Terraform. This prevents Terraform from continuing and lets the user know the action did not work as expected.)

Import `TYLPersistent` and define your subclass:

.. code:: python

  from abc_tylstore import TYLPersistent
  class MyPersistentBackend(TYLPersistent):
      def __init__(self, environment, constants, **kwargs):
      .
      .
      .

Implement the following functions in your class:

- :python:`__init__(self, environment, constants, **kwargs):`
    - :python:`environment` every environment will get a separate instance of your class and as a result, this value should be treated as a constant. Use this value to keep environment states isolated from each other. For example, if you are saving your Terraform states into plain text files, you'd likely want your file name to be something like :bash:`<environment>_terraform.tfstate`
    - :python:`constants` a python class containing constant values. These values are partly populated by :bash:`config.yaml` as key:value pairs. For example, if you set :yaml:`MY_BACKEND_FOO: 'Hello, World!'` in :bash:`config.yaml`, you can access the string value with `constants.MY_BACKEND_FOO`. This allows you to configure your backend module without the need of a separate configuration file.
    - :python:`**kwargs` It is recommended to add this to help ensure forward compatibility of your module with future versions of PyTerraBackTYL.
- :python:`def set_locked(self, state_obj, **kwargs):`
    - :python:`state_obj` Unpacked JSON (:python:`dict`) with the specifics on who is putting a lock on the environment.
    - :python:`**kwargs` includes :python:`raw` which contains the original JSON string (:python:`str`) value.
    - **RETURNS**: value that evaluates to :python:`True` on a successful lock; value that evaluates to :python:`False` when someone else is already holding the lock.
- :python:`def set_unlocked(self, state_obj, **kwargs):`
    - :python:`state_obj` Unpacked JSON (:python:`dict`) with the specifics on who is unlocking the environment. The :python:`ID` value should match the one provided when lock was created. However, when a user issues a :bash:`terraform force-unlock <ID value>` command, the ID is not currently being passed to the backend. Validating the ID in this function will make forcing an unlock impossible until HashiCorp addresses this deficiency.
    - :python:`**kwargs` includes :python:`raw` which contains the original JSON string (:python:`str`) value.
    - **RETURNS**: value that evaluates to :python:`True` on a successful unlock; value that evaluates to :python:`False` when the environment is NOT still locked (logs warning message).
- :python:`def get_lock_state(self):`
    - **RETURNS**: The string (:python:`str`) or JSON compatible object of the lock (the value received in :python:`set_locked()`). Return and empty string when no lock is held.
- :python:`def store_tfstate(self, tfstate_obj, **kwargs):`
    - :python:`tfstate_obj` Unpacked JSON (:python:`dict`) which specifies the current terraform state (:bash:`terraform.tfstate`)
    - :python:`**kwargs` includes :python:`raw` which contains the original JSON string (:python:`str`) value.
    - No return value. Return :python:`None` if needed.
- :python:`def get_tfstate(self):`
    - **RETURNS**: The string (:python:`str`) or JSON compatible object of the Terraform state (the value received in :python:`store_tfstate()`).
- :python:`def backend_status(self):` *OPTIONAL*
    - **RETURNS**: A JSON compatible object containing health and status information about the backend. This is a good place to report where data is being stored and lock state for the environment.
