import os
import logging

from itertools import cycle
from Crypto import Random, Cipher
from abc_tylstore import TYLPersistent, TYLHelpers

__version__ = "0.2.1"


class _lazyAES(object):
    def __init__(self, key):
        c = cycle(key)
        self.key = "".join([next(c) for x in range(0, 32)])

    def encrypt(self, raw):
        raw += " " * (Cipher.AES.block_size - len(raw) % Cipher.AES.block_size)
        iv = Random.new().read(Cipher.AES.block_size)
        cipher = Cipher.AES.new(self.key, Cipher.AES.MODE_CBC, iv)
        return iv + cipher.encrypt(raw)

    def decrypt(self, enc):
        iv = enc[: Cipher.AES.block_size]
        cipher = Cipher.AES.new(self.key, Cipher.AES.MODE_CBC, iv)
        return cipher.decrypt(enc[Cipher.AES.block_size :]).decode().strip()

    def __setitem__(self, filename, value):
        fout = open(filename, "wb")
        fout.write(self.encrypt(value))
        fout.close()

    def __getitem__(self, filename):
        fin = open(filename, "rb")
        value = fin.read()
        fin.close()
        return self.decrypt(value)

    def __delitem__(self, filename):
        os.remove(filename)

    def __contains__(self, filename):
        return os.path.isfile(filename)


class AESBackend(TYLPersistent):
    def __init__(self, environment, constants, **kwargs):
        self.C = constants
        self.ENV = environment

        self.tfstate_filename = os.sep.join(
            [self.C.AES_DATA_PATH, self.ENV + self.C.AES_TFSTATE_FILENAME]
        )
        self.tflock_filename = os.sep.join(
            [self.C.AES_DATA_PATH, self.ENV + self.C.AES_TFLOCK_FILENAME]
        )
        self.tfstate_aes = _lazyAES(self.C.AES_SECRET_KEY)

        if self.tfstate_filename not in self.tfstate_aes:
            self.tfstate_aes[self.tfstate_filename] = ""

    def set_locked(self, state_obj, **kwargs):
        """
        :param state_obj: Object (from json) with the lock ID and details of who made the lock.
        :param kwargs: Includes 'raw' which has the json text as a string (str)
        :return: True on successful lock, False if something prevented the lock from happening.
        """
        if self.tflock_filename in self.tfstate_aes:
            logging.warning(
                "Failed to obtain lock for ENV %s, already locked" % self.ENV
            )
            return False

        logging.info("Locking ENV %s" % self.ENV)
        self.tfstate_aes[self.tflock_filename] = kwargs["raw"]
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
        if self.tflock_filename in self.tfstate_aes:
            del self.tfstate_aes[self.tflock_filename]
            return True
        logging.warning(
            "Failed to release lock for ENV %s, already unlocked!" % self.ENV
        )
        return False

    def get_lock_state(self):
        """
        :return: The request/JSON string provided by terraform of the current lock (the value received in set_locked()),
                 Return an empty string if there is no lock.
        """
        if self.tflock_filename in self.tfstate_aes:
            return self.tfstate_aes[self.tflock_filename]
        return ""

    def store_tfstate(self, tfstate_obj, **kwargs):
        """
        :param tfstate_obj: JSON string of the current terraform.tfstate file.
        :param kwargs: Includes 'raw' which has the json text as a string (str)
        """
        self.tfstate_aes[self.tfstate_filename] = kwargs["raw"]
        logging.debug("Saved state file for env %s" % self.ENV)

    def get_tfstate(self):
        """
        :return: Object or JSON formatted string of the current terraform.tfstate file (the value received in store_tfstate()).
        """
        return self.tfstate_aes[self.tfstate_filename]

    def backend_status(self):
        """
        :return: Health and status information in a JSON compatible format. This function is optional and may be omitted.
        """
        return {
            "filename": self.tfstate_filename,
            "locked": self.tflock_filename in self.tfstate_aes,
            "built_hosts": TYLHelpers.get_hostnames_from_tfstate(
                self.tfstate_aes[self.tfstate_filename]
            ),
        }
