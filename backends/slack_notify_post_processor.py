import requests

from collections import defaultdict
from abc_tylstore import TYLNonpersistent, TYLHelpers


class SlackNotifyPostProcessor(TYLNonpersistent):
    def __init__(self, environment, constants, **kwargs):
        self.ENV = environment
        self.C = constants
        self.lock_info = {}

    def _post_to_slack(self, message, operation, channel=None):
        message = "_Environment %s:_ %s\n%s" % (self.ENV, operation, message)

        payload = {
            "username": self.C.SLACK_NOTIFY_USERNAME,
            "icon_url": self.C.SLACK_NOTIFY_USER_IMAGE_URI,
            "text": message,
        }

        if channel:
            if not channel.startswith("#"):
                channel = "#%s" % channel
            payload["channel"] = channel

        requests.post(self.C.SLACK_WEBHOOK_URI, json=payload)

    def on_locked(self, state_obj, **kwargs):
        """
        :param state_obj: Object (from json) with the lock ID and details of who made the lock.
        :param kwargs: Includes 'raw' json object as text (str)
        :return: None
        """
        self.lock_info = state_obj
        if self.lock_info["Operation"] in self.C.SLACK_NOTIFICATIONS_ON_TF_ACTIONS:
            self._post_to_slack(
                self.C.SLACK_NOTIFY_FORMAT.format(**defaultdict(str, self.lock_info)),
                "*LOCKED* :lock:",
            )

    def on_unlocked(self, state_obj, **kwargs):
        """
        :param state_obj: Object (from json) with the lock ID and details of who made the lock.
        :param kwargs: Includes 'raw' json object as text (str)
        """
        if (
            self.lock_info["Operation"] in self.C.SLACK_NOTIFICATIONS_ON_TF_ACTIONS
            and self.C.SLACK_NOTIFY_UNLOCK
        ):
            self._post_to_slack(
                self.C.SLACK_NOTIFY_UNLOCK_FORMAT.format(
                    **defaultdict(str, self.lock_info)
                ),
                "*Unlock* :unlock:",
            )
        self.lock_info = {}

    def process_tfstate(self, tfstate_obj, **kwargs):
        """
        :param tfstate_obj: JSON string of the current terraform.tfstate file.
        :param kwargs: Includes 'raw' json object as text (str)
        :return:
        """
        if self.C.SLACK_NOTIFY_HOST_LIST:
            new_hosts = ", ".join(TYLHelpers.get_hostnames_from_tfstate(tfstate_obj))
            if new_hosts:
                self._post_to_slack(new_hosts, "Created Hosts :lock_with_ink_pen: ")

    def post_processor_status(self):
        """
        :return: Health and status object in a JSON compatible format.
        """
        return {
            "locked": bool(self.lock_info),
            "slack_user_image_uri": self.C.SLACK_NOTIFY_USER_IMAGE_URI,
            "slack_username": self.C.SLACK_NOTIFY_USERNAME,
        }
