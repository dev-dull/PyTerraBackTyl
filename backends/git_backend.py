import os
import tempfile
from CONSTS import C
from dulwich import porcelain
from abc_tylstore import TYLStore


class GitBackend(TYLStore):
    def __init__(self, parent):
        self.parent = parent
        self.working_dir = C.GIT_WORKING_PATH or tempfile.mkdtemp()
        if self.working_dir.endswith(os.sep):
            self.working_dir = self.working_dir[0:-1]
        print('jflaksdjflksadjflsadjflksd', self.working_dir)

    def set_locked(self, request):
        # create lock file
        # write request.data to file
        # commit/push lock file
        return True

    def set_unlocked(self, request):
        # append the change log
        # git rm lock file
        # commit/push the rm
        return True

    def get_lock_state(self):
        # pull the repo
        # check for lock file
        # return contents of lock file || None
        pass

    def store_tfstate(self, tfstate_text):
        file_name = os.sep.join([self.working_dir, C.TFSTATE_FILE_NAME])
        try:
            t = self.parent.request.data.decode()
            fout = open(file_name, 'w')
            fout.write(t)
            fout.close()
            print('Files:', self.parent.request.data)
        except Exception as e:
            return False
        return True

    def get_tfstate(self):
        return 'buh-aye'