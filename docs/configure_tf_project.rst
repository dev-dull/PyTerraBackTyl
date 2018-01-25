.. _configure_tf_project:

.. role:: bash(code)
  :language: bash

.. role:: yaml(code)
  :language: yaml

Configure your Terraform project to use the PyTerraBackTYL HTTP backend
=======================================================================

In your project, configure the HTTP backend service, remember to change the following details:

- **Your environment value (e.g. `DEVTEST` in `env=DEVTEST`) MUST be unique for each environment (Terraform project)** and the three URLs in the configuration below must all have the same environment value set.
- Change :bash:`http://` to :bash:`https://` if you created your encryption keys and enabled SSL in :bash:`config.yaml` (but the :bash:`backend` line should remain :bash:`"http"`)
- Change :bash:`localhost` to the host or IP where the PyTerrBackTYL service is running.
- Note that Terraform expects the :bash:`skip_cert_verification` value to be a string. Check on Issue 17098_ to see if this bug has been fixed.

.. _17098: https://github.com/hashicorp/terraform/issues/17098

.. code::

    terraform {
      backend "http" {
        address = "http://localhost:2442/?env=DEVTEST"
        lock_address = "http://localhost:2442/lock?env=DEVTEST"
        unlock_address = "http://localhost:2442/unlock?env=DEVTEST"
        skip_cert_verification = "true"
      }
    }


Start and test the PyTerraBackTYL service
=========================================
- :bash:`cd` to where you have PyTerrBackTYL installed (e.g. :bash:`cd /opt/pytterrabacktyl/PyTerrBackTyl`)
- Switch to the service account (e.g. :bash:`sudo su tfbackendsvc`)
- A start script is provided, but for the first test, it is recommended you start the script with :bash:`python3 pyterrabacktyl.py` so that logging will be printed to the screen.
- In a new shell, validate that the service is responding with :bash:`curl -sk http://localhost:2442/state` - remember to change 'http' to 'https' if you enabled SSL. Output should look similar to the following
    - .. code:: json

        {
          "backend_module": "aes_backend.AESBackend",
          "environments": [],
          "post_processor_modules": [
            "slack_notify_post_processor.SlackNotifyPostProcessor"
          ]
        }
- Run :bash:`terraform init` for your Terraform project. If this is an existing project, answer "yes" to migrate the state to "http"
- Check logging for errors and if no errors have been logged, check :bash:`curl -sk http://localhost:2442/state` again. It should now look similar to the following
    - .. code:: json

        {
          "backend_module": "aes_backend.AESBackend",
          "environments": [
            {
              "backend_status": {
                "built_hosts": [],
                "filename": "data/DEVTEST_aes_tfstate.bin",
                "locked": false
              },
              "environment_name": "DEVTEST",
              "http_state": 200,
              "lock_state": "UNLOCKED",
              "post_processors": [
                {
                  "num_errors_logged": 0,
                  "post_processor_module": "SlackNotifyPostProcessor",
                  "post_processor_status": {
                    "locked": false,
                    "slack_user_image_uri": "http://www.devdull.lol/pyterrabacktyl/pyterrabacktyl_logo_square.png",
                    "slack_username": "PyTerraBackTYL"
                  },
                  "recent_logged_error": ""
                }
              ]
            }
          ],
          "post_processor_modules": [
            "slack_notify_post_processor.SlackNotifyPostProcessor"
          ]
        }
