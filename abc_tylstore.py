import abc


class TYLStore(object):
    __metaclass__ = abc.ABCMeta
    lock_state = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx IT\'S A TRAP!'

    @abc.abstractmethod
    def set_locked(self, request):
        """
        :param request: JSON string with the lock ID and details of who made the lock.
        :return: True on successful lock, False if something prevented the lock from happening.
        """
        pass

    @abc.abstractmethod
    def set_unlocked(self, request):
        """
        :param request: JSON string with the lock ID and details of who made the lock.
        """
        pass

    @abc.abstractmethod
    def get_lock_state(self):
        """
        :return: The request/JSON string provided by terraform of the current lock, None if there is no lock.
        """
        pass

    @abc.abstractmethod
    def store_tfstate(self, tfstate_text):
        """
        :param tfstate_text: JSON string of the current terraform.tfstate file.
        :return:
        """
        pass

    @abc.abstractmethod
    def get_tfstate(self):
        """
        :return: JSON string of the current terraform.tfstate file.
        """
        pass
