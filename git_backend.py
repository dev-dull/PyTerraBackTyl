import tempfile
from dulwich import porcelain
from abc_tylstore import TYLStore


class GitBackend(TYLStore):
    def __init__(self, parent):
        self.parent = parent

    def set_locked(self, fingerprint):
        pass

    def set_unlocked(self, fingerprint):
        pass

    def get_lock_state(self):
        pass

    def store_tfstate(self, tfstate_text):
        return 'hi'

    def get_tfstate(self):
        return 'buh-aye'