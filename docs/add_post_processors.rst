.. _add_post_processors:

.. role:: bash(code)
  :language: bash

.. role:: yaml(code)
  :language: yaml

Optional: Add Post-Processors (nonpersistent backends)
======================================================
PyTerraBackTYL allows for post-processor or nonpersistant plugins. These plugins are meant to do additional work based on the content of the current lock or the current Terraform state. PyTerrBackTYL comes with a nonpersistent backend that pushes notifications into Slack chat rooms, and other users have successfully used post-processors to automatically add and remove hosts from Zenoss monitoring with every :bash:`terraform apply` and :bash:`terraform destroy`

.. toctree::
    :maxdepth: 2

    slack_post_processor
    custom_post_processor
