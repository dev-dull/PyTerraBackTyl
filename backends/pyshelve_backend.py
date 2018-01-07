import os
import shelve
import logging

from abc_tylstore import TYLPersistent, TYLHelpers

__version__ = '0.2.0'


class _lazyShelf(object):
    def __init__(self, filename):
        self.filename = filename

    def __setitem__(self, key, value):
        sf = shelve.open(self.filename)
        sf[key] = value
        sf.close()

    def __getitem__(self, key):
        sf = shelve.open(self.filename)
        value = sf[key]
        sf.close()
        return value

    def __delitem__(self, key):
        sf = shelve.open(self.filename)
        del sf[key]
        sf.close()

    def __contains__(self, key):
        sf = shelve.open(self.filename)
        value = key in sf
        sf.close()
        return value


class PyShelveBackend(TYLPersistent):
    def __init__(self, environment, constants, **kwargs):
        self.C = constants
        self.C.TFSTATE_KEYWORD = 'TFSTATE'
        self.C.LOCK_STATE_KEYWORD = 'LOCK_STATE'
        self.ENV = environment

        self.tfstate_file_name = os.sep.join([self.C.PYSHELVE_DATA_PATH, self.ENV+self.C.PYSHELVE_DB_FILE_NAME])
        self.tfstate_shelf = _lazyShelf(self.tfstate_file_name)

        if self.C.TFSTATE_KEYWORD not in self.tfstate_shelf:
            self.tfstate_shelf[self.C.TFSTATE_KEYWORD] = ''

    def set_locked(self, state_obj, **kwargs):
        """
        :param state_obj: Object (from json) with the lock ID and details of who made the lock.
        :param kwargs: Includes 'raw' which has the json text as a string (str)
        :return: True on successful lock, False if something prevented the lock from happening.
        """
        if self.C.LOCK_STATE_KEYWORD in self.tfstate_shelf:
            logging.warning('Failed to obtain lock for ENV %s, already locked' % self.ENV)
            return False

        logging.info('Locking ENV %s' % self.ENV)
        self.tfstate_shelf[self.C.LOCK_STATE_KEYWORD] = state_obj
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
        if self.C.LOCK_STATE_KEYWORD in self.tfstate_shelf:
            del self.tfstate_shelf[self.C.LOCK_STATE_KEYWORD]
            return True
        logging.warning('Failed to release lock for ENV %s, already unlocked!' % self.ENV)
        return False

    def get_lock_state(self):
        """
        :return: The request/JSON string provided by terraform of the current lock (the value received in set_locked()),
                 Return an empty string if there is no lock.
        """
        if self.C.LOCK_STATE_KEYWORD in self.tfstate_shelf:
            return self.tfstate_shelf[self.C.LOCK_STATE_KEYWORD]
        return ''

    def store_tfstate(self, tfstate_obj, **kwargs):
        """
        :param tfstate_obj: JSON string of the current terraform.tfstate file.
        :param kwargs: Includes 'raw' which has the json text as a string (str)
        """
        self.tfstate_shelf[self.C.TFSTATE_KEYWORD] = tfstate_obj
        logging.debug('Saved state file for env %s' % self.ENV)

    def get_tfstate(self):
        """
        :return: Object or JSON formatted string of the current terraform.tfstate file (the value received in store_tfstate()).
        """
        return self.tfstate_shelf[self.C.TFSTATE_KEYWORD]

    def backend_status(self):
        """
        :return: Health and status information in a JSON compatible format. This function is optional and may be omitted.
        """
        return {
            'filename': self.tfstate_file_name,
            'tfstate_obj_key': self.C.TFSTATE_KEYWORD,
            'lock_state_obj_key': self.C.LOCK_STATE_KEYWORD,
            'tfstate_exists': bool(self.tfstate_shelf[self.C.TFSTATE_KEYWORD]),
            'locked': self.C.LOCK_STATE_KEYWORD in self.tfstate_shelf,
            'built_hosts': TYLHelpers.get_hostnames_from_tfstate(self.tfstate_shelf[self.C.TFSTATE_KEYWORD])
        }
