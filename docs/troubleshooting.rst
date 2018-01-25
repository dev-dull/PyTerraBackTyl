.. _troubleshooting:

.. role:: bash(code)
  :language: bash

.. role:: yaml(code)
  :language: yaml

Basic PyTerraBackTYL Troubleshooting
====================================
- As always, check the log. If you haven't modified the default start script, a new subdirectory called :bash:`logs` will be created in the same location as the script.
- Check what information is found in the :bash:`/state` endpoint. You can monitor state changes with the command :bash:`watch -d "curl -s http://localhost:2442/state"`.
