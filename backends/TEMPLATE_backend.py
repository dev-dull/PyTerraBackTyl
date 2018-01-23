import os
import logging

from abc_tylstore import TYLPersistent, TYLHelpers

__version__ = '0.1.0'


class TemplateBackend(TYLPersistent):
    def __init__(self, environment, constants, **kwargs):
        self.C = constants
        self.ENV = environment

        # TODO: remove the below 'if' block when using this file as a starting point for your own custom backend.
        if not hasattr(self.C, 'YES_I_KNOW_WHAT_I_AM_DOING'):
            raise NotImplementedError('The TEMPLATE_backend is only intended to be used as a starting point for '
                                      'developing new backend modules and should not be used directly!')

        # When persisting data (e.g. writing a file to disk) you need to use ENV to keep locking and state separated.
        # In this instance, we are just illustrating how this separation should be achieved.
        # For example, you might use `'%s_TFSTATE' % self.ENV` as a file name.
        self.TFSTATE_KEYWORD = '%s_TFSTATE' % self.ENV
        self.LOCK_STATE_KEYWORD = '%s_LOCK_STATE' % self.ENV

        self.tfstate = {}

        # Create an initial empty state so we don't have to check for one with every call of get_tfstate()
        if self.TFSTATE_KEYWORD not in self.tfstate:
            self.tfstate[self.TFSTATE_KEYWORD] = ''

    def set_locked(self, state_obj, **kwargs):
        """
        :param state_obj: Object (from json) with the lock ID and details of who made the lock.
        :param kwargs: Includes 'raw' which has the json text as a string (str)
        :return: True on successful lock, False if something prevented the lock from happening.
        """
        if self.LOCK_STATE_KEYWORD in self.tfstate:
            logging.warning('Failed to obtain lock for ENV %s, already locked' % self.ENV)
            return False

        logging.info('Locking ENV %s' % self.ENV)
        self.tfstate[self.LOCK_STATE_KEYWORD] = state_obj
        return True

    def set_unlocked(self, state_obj, **kwargs):
        """
        :param state_obj: Object (from json) with the lock ID and details of who made the lock.
        :param kwargs: Includes 'raw' which has the json text as a string (str)
        :return: True on successful unlock.
                 False when the environment was somehow already unlocked.
                 A return value of False should never happen and indicates a bug with the backend or PyTerraBackTYL.
        """
        # Terraform doesn't currently send the lock ID when a force-unlock is done.
        # If they fix that, then we should compare lock IDs before unlocking.
        if self.LOCK_STATE_KEYWORD in self.tfstate:
            del self.tfstate[self.LOCK_STATE_KEYWORD]
            return True
        logging.warning('Failed to release lock for ENV %s, already unlocked!' % self.ENV)
        return False

    def get_lock_state(self):
        """
        :return: The request/JSON string provided by terraform of the current lock (the value received in set_locked()),
                 Return an empty string if there is no lock.
        """
        if self.LOCK_STATE_KEYWORD in self.tfstate:
            return self.tfstate[self.LOCK_STATE_KEYWORD]
        return ''

    def store_tfstate(self, tfstate_obj, **kwargs):
        """
        :param tfstate_obj: JSON string of the current terraform.tfstate file.
        :param kwargs: Includes 'raw' which has the json text as a string (str)
        """
        self.tfstate[self.TFSTATE_KEYWORD] = tfstate_obj
        logging.debug('Saved state file for env %s' % self.ENV)

    def get_tfstate(self):
        """
        :return: Object or JSON formatted string of the current terraform.tfstate file (the value received in store_tfstate()).
        """
        return self.tfstate[self.TFSTATE_KEYWORD]

    def backend_status(self):
        """
        :return: Health and status information in a JSON compatible format. This function is optional and may be omitted.
        """
        return {
            'tfstate_obj_key': self.TFSTATE_KEYWORD,
            'lock_state_obj_key': self.LOCK_STATE_KEYWORD,
            'tfstate_exists': bool(self.tfstate[self.TFSTATE_KEYWORD]),
            'locked': self.LOCK_STATE_KEYWORD in self.tfstate,
            'built_hosts': TYLHelpers.get_hostnames_from_tfstate(self.tfstate[self.TFSTATE_KEYWORD])
        }
