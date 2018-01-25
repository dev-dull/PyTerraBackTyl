.. _slack_post_processor:

.. role:: bash(code)
  :language: bash

.. role:: yaml(code)
  :language: yaml

Configuring the Slack Postprocessor
===================================

- :yaml:`SLACK_WEBHOOK_URI: https://hooks.slack.....`
    - The webhook URI that will be used to push chat notifications into your Slack channel.
    - You can create a new webook URI by signing into Slack from your web browser and then visiting the `new webhook`_ page.
- :yaml:`SLACK_NOTIFY_USER_IMAGE_URI: http://www.....'`
    - The user icon that will appear in the Slack channel
- :yaml:`SLACK_NOTIFY_USERNAME: PyTerraBackTYL`
    - The username that will appear in the Slack channel
- :yaml:`SLACK_NOTIFICATIONS_ON_TF_ACTIONS: [OperationTypeApply, OperationTypePlan]`
    - The type of events the Slack channel should be notified for.
    - Note that :bash:`terraform apply` and :bash:`terraform destroy` both send PyTerrBackTYL the action type of :yaml:`OperationTypeApply`
    - More than likely you will want to comment out :yaml:`OperationTypePlan` notifications
- :yaml:`SLACK_NOTIFY_HOST_LIST: true`
    - When set to true, and :yaml:`HELPER_HOSTNAME_QUERY_MAP` has been correctly configured for the Terraform provider being used, the Slack channel will be updated with a list of newly created hosts.
- :yaml:`SLACK_NOTIFY_UNLOCK: true`
    - When set to true, the Slack channel will be notified when a user has released their lock.
- :yaml:`SLACK_NOTIFY_FORMAT: "_Who:_ *{Who}*\n_Operation:_ *{Operation}*\n_Version:_ {Version}\n_ID:_ {ID}"`
    - What details and formatting to use to update the Slack channel with.
    - The use of double quotes (e.g. "double quotes") is required for escape sequences like \n (newline) to work.
    - valid values (e.g. the :bash:`{Who}` in the above) are:
        - ID: An ID created by Terraform.
        - Operation: The Terraform operation being carried out (plan, apply, etc.)
        - Info: (check terraform documentation)
        - Who: The username and hostname who initiated the terraform command.
        - Version: The version of Terraform that was used.
        - Created: Timestamp of when the terraform command ws run.
        - Path: (check terraform documentation)
- :yaml:`SLACK_NOTIFY_UNLOCK_FORMAT: "_Who:_ *{Who}*\n_ID:_ {ID}"`
    - Similar to the previous configuration option, but only when the lock is released.

.. _new webhook: https://my.slack.com/services/new/incoming-webhook/

Full example configuration for SlackNotifyPostProcessor
-------------------------------------------------------

.. code:: yaml

    POST_PROCESS_CLASSES:
    - 'slack_notify_post_processor.SlackNotifyPostProcessor'

    ##
    ##  slack_notify_post_processor.SlackNotifyPostProcessor configuration
    ##

    # This should be the webhook for the 'random' room in the PyTerraBackTYL Slack.
    SLACK_WEBHOOK_URI: https://hooks.slack.com/services/XXXXXXXXX/YYYYYYYYY/ZZZZZZZZZZZZZZZZZZZZZZZZ

    SLACK_NOTIFY_USER_IMAGE_URI: http://www.devdull.lol/pyterrabacktyl/pyterrabacktyl_logo_square.png
    # Here's the terraform logo if you prefer: https://avatars0.githubusercontent.com/u/11051457?s=400&v=4
    SLACK_NOTIFY_USERNAME: PyTerraBackTYL

    # Which `terraform <command>` operations to notify Slack for.
    SLACK_NOTIFICATIONS_ON_TF_ACTIONS:
    - OperationTypeApply
    - OperationTypePlan

    SLACK_NOTIFY_HOST_LIST: true
    SLACK_NOTIFY_UNLOCK: true

    # The use of double quotes (e.g. "hello\nworld") is required for '\n' to be evaluated as a newline.
    SLACK_NOTIFY_FORMAT: "_Who:_ *{Who}*\n_Operation:_ *{Operation}*\n_Version:_ {Version}\n_ID:_ {ID}"
    SLACK_NOTIFY_UNLOCK_FORMAT: "_Who:_ *{Who}*\n_ID:_ {ID}"
