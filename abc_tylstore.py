import abc
from CONSTS import C


class TYLHelpers(object):
    @classmethod
    def get_hostnames_from_tfstate(cls, json_obj):
        pass


class TYLPersistent(object):
    __metaclass__ = abc.ABCMeta
    # TODO: Assignment to this variable from pyterrabacktyl is probably duck-typing in a new variable.
    __lock_state__ = C.LOCK_STATE_UNLOCKED

    @abc.abstractmethod
    def set_locked(self, state_obj, raw=''):
        """
        :param state_obj: Object (from json) with the lock ID and details of who made the lock.
        :param raw: The raw json text
        :return: True on successful lock, False if something prevented the lock from happening.
        """
        pass

    @abc.abstractmethod
    def set_unlocked(self, state_obj, raw=''):
        """
        :param state_obj: Object (from json) with the lock ID and details of who made the lock.
        :param raw: The raw json text
        """
        pass

    @abc.abstractmethod
    def get_lock_state(self):
        """
        :return: The request/JSON string provided by terraform of the current lock, None if there is no lock.
        """
        pass

    @abc.abstractmethod
    def store_tfstate(self, tfstate_obj, raw=''):
        """
        :param tfstate_obj: JSON string of the current terraform.tfstate file.
        :param raw: The raw json text
        :return:
        """
        pass

    @abc.abstractmethod
    def get_tfstate(self):
        """
        :return: JSON string of the current terraform.tfstate file.
        """
        pass


class TYLNonpersistent(object):
    __metaclass__ = abc.ABCMeta
    # TODO: Assignment to these variables from pyterrabacktyl is probably duck-typing in a new variable.
    __logged_errors__ = 0
    __recent_error__ = ''

    @abc.abstractmethod
    def on_locked(self, state_obj, raw=''):
        """
        :param state_obj: Object (from json) with the lock ID and details of who made the lock.
        :param raw: The raw json text
        :return: None
        """
        pass

    @abc.abstractmethod
    def on_unlocked(self, state_obj, raw=''):
        """
        :param state_obj: Object (from json) with the lock ID and details of who made the lock.
        :param raw: The raw json text
        """
        pass

    @abc.abstractmethod
    def process_tfstate(self, tfstate_obj, raw=''):
        """
        :param tfstate_obj: JSON string of the current terraform.tfstate file.
        :param raw: The raw json text
        :return:
        """
        pass