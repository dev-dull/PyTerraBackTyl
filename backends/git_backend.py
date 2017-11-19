import tempfile
from dulwich import porcelain
from abc_tylstore import TYLStore


class GitBackend(TYLStore):
    def __init__(self, parent):
        self.parent = parent
        self.working_dir = self.parent.C.GIT_WORKING_PATH or tempfile.mkdtemp()
        self.working_dir = self.working_dir[0:-1] if self.working_dir.endswith('/') else self.working_dir

    def set_locked(self, fingerprint):
        return True

    def set_unlocked(self, fingerprint):
        pass

    def get_lock_state(self):
        pass

    def store_tfstate(self, tfstate_text):
        try:
            t = self.parent.request.data.decode()
            fout = open(self.parent.C.TFSTATE_FILE_NAME, 'w')
            fout.write(t)
            fout.close()
            print('Files:', self.parent.request.data)
        except Exception as e:
            return False
        return True

    def get_tfstate(self):
        return 'buh-aye'