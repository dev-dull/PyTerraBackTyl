.. PyTerraBackTYL documentation master file, created by
   sphinx-quickstart on Wed Jan 24 11:30:17 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. role:: python(code)
  :language: python



PyTerraBackTYL
==============
.. image:: /_static/pyterrabacktyl_logo_v2.png
   :align: center
   :alt: PyTerraBackTYL logo

About:
------
PyTerraBackTYL is an HTTP backend for Terraform that allows you to control how locking and state are managed. You can use one of the provided persistent plugins to save state to disk, store state in a Git repository, or encrypt the state to disk with 256bit CBC mode AES.

You can also create your own persistent backend plugin to handle locks and store state however you like by implementing the `TYLPersistent` abstract class.

Additionally, you can implement the `TYLNonpersistent` abstract class to perform actions based on lock status and Terraform state content. A nonpersistent plugin to notify a Slack chatroom of changes is provided, but users have also created nonpersistant plugins that automatically add or remove hosts from monitoring, and update load-balancer configurations.

Installation:
-------------
.. toctree::
    :maxdepth: 2

    install
    picking_a_backend
    configure_tf_project
    add_post_processors
    troubleshooting
    thanks



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
