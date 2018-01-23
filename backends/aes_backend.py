import os
import logging

from itertools import cycle
from Crypto.Cipher import AES
from abc_tylstore import TYLPersistent

__version__ = '0.1.0'


# https://www.dlitz.net/software/pycrypto/api/current/Crypto.Cipher.AES-module.html
def _lazy_encrypt(key, iv, data, pad_chr=' '):
    key, iv = _key_iv(key, iv)
    data += pad_chr * (16 - len(data) % 16)  # pad the end with spaces
    return AES.new(key, AES.MODE_CBC, iv).encrypt(data)


def _lazy_decrypt(key, iv, data):
    if data:
        key, iv = _key_iv(key, iv)
        return AES.new(key, AES.MODE_CBC, iv).decrypt(data).decode().strip()
    return ''


def _key_iv(key, iv):
    # Make it so that the user doesn't have to know how many bytes long these values have to be.
    c = cycle(key)
    key = ''.join([next(c) for x in range(0, 32)])

    c = cycle(iv)
    iv = ''.join([next(c) for x in range(0, 16)])

    return key, iv


class AESBackend(TYLPersistent):
    def __init__(self, environment, constants, **kwargs):
        self.C = constants
        self.ENV = environment

        self.lockfile = os.sep.join([self.C.AES_WORKING_PATH, self.ENV+'_LOCKED.bin'])
        self.statefile = os.sep.join([self.C.AES_WORKING_PATH, self.ENV + '_tfstate.bin'])

        if not os.path.isfile(self.lockfile):
            fout = open(self.statefile, 'wb')
            fout.write(b'')
            fout.close()

    def set_locked(self, state_obj, **kwargs):
        """
        :param state_obj: Object (from json) with the lock ID and details of who made the lock.
        :param kwargs: Includes 'raw' which has the json text as a string (str)
        :return: True on successful lock, False if something prevented the lock from happening.
        """
        if os.path.isfile(self.lockfile):
            logging.warning('Failed to obtain lock for ENV %s, already locked' % self.ENV)
            return False

        logging.info('Locking ENV %s' % self.ENV)
        fout = open(self.lockfile, 'wb')
        fout.write(_lazy_encrypt(self.C.AES_SECRET_KEY, self.C.AES_INIT_VECTOR, kwargs['raw']))
        fout.close()
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
        if os.path.isfile(self.lockfile):
            os.remove(self.lockfile)
            return True
        logging.warning('Failed to release lock for ENV %s, already unlocked!' % self.ENV)
        return False

    def get_lock_state(self):
        """
        :return: The request/JSON string provided by terraform of the current lock (the value received in set_locked()),
                 Return an empty string if there is no lock.
        """
        if os.path.isfile(self.lockfile):
            fin = open(self.lockfile, 'rb')
            lock_data = fin.read()
            fin.close()

            return _lazy_decrypt(self.C.AES_SECRET_KEY, self.C.AES_INIT_VECTOR, lock_data)
        return ''

    def store_tfstate(self, tfstate_obj, **kwargs):
        """
        :param tfstate_obj: JSON string of the current terraform.tfstate file.
        :param kwargs: Includes 'raw' which has the json text as a string (str)
        """
        fout = open(self.statefile, 'wb')
        fout.write(_lazy_encrypt(self.C.AES_SECRET_KEY, self.C.AES_INIT_VECTOR, kwargs['raw']))
        fout.close()
        logging.debug('Saved state file for env %s' % self.ENV)

    def get_tfstate(self):
        """
        :return: Object or JSON formatted string of the current terraform.tfstate file (the value received in store_tfstate()).
        """
        fin = open(self.statefile, 'rb')
        tfstate_data = fin.read()
        fin.close()
        return _lazy_decrypt(self.C.AES_SECRET_KEY, self.C.AES_INIT_VECTOR, tfstate_data)

    def backend_status(self):
        """
        :return: Health and status information in a JSON compatible format. This function is optional and may be omitted.
        """
        return {
            'filename': self.statefile,
            'tfstate_exists': os.path.isfile(self.statefile),
            'locked': os.path.isfile(self.lockfile),
        }
