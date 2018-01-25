.. _picking_a_backend:

.. role:: python(code)
  :language: python

Pick a Persistent Backend
=========================
PyTerraBackTYL currently comes with three different options for managing the Terraform state file. Each one has different pros and cons depending on your use-case.

- PyShelve
    - This backend plugin will persist the Terraform locking and state as a Python object to disk.
    - Pros: Very fast, easy to configure
    - Cons: Difficult to visually inspect the contents of locking and state.
- Git
    - This backend plugin will store Terraform locking and state into separate branches of a Git repository
    - Pros: Great for teams, easy to visually inspect state, easy to track changes to state, audit log of changes
    - Cons: Requires a private Git repository, slow, difficult to configure
- AES
    - This plugin will encrypt Terraform locking and state with 256bit CBC mode AES encryption, and then persist the encrypted data to disk
    - Pros: Secure, relatively fast, easy to configure
    - Cons: Difficult to visually inspect the contents of locking and state

You can also create your own custom backend plugin by implementing the :python:`TYLPersistent` abstract class.

.. toctree::
    :maxdepth: 2

    pyshelve_backend
    git_backend
    aes_backend
    custom_backend
