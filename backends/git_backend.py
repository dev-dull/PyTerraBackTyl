import os
import logging
import tempfile
from CONSTS import C
from dulwich import porcelain
from abc_tylstore import TYLStore


class GitBackend(TYLStore):
    def __init__(self, environment):
        self.ENV = environment

        self.working_dir = C.GIT_WORKING_PATH or tempfile.mkdtemp()
        if self.working_dir.endswith(os.sep):
            self.working_dir = self.working_dir[0:-1]
        self.working_dir = os.sep.join([self.working_dir, self.ENV])
        self.tfstate_file_name = os.sep.join([self.working_dir, C.TFSTATE_FILE_NAME])

        self.__make_repo()

    def __make_repo(self):
        if not os.path.exists(self.working_dir):
            porcelain.clone(C.GIT_REPOSITORY, target=self.working_dir)
        repo = porcelain.open_repo(self.working_dir)

        # if this is a new repo with no head, do a commit before creating the branch.

        if self.ENV not in porcelain.branch_list(self.working_dir):
            porcelain.branch_create(self.working_dir, self.ENV)

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
        fout = open(self.tfstate_file_name, 'w')
        fout.write(tfstate_text)
        fout.close()
        logging.debug('Saved state file %s' % self.tfstate_file_name)
        print('Files:', self.tfstate_file_name)

    def get_tfstate(self):
        try:
            logging.debug('Reading state file %s' % self.tfstate_file_name)
            fin = open(self.tfstate_file_name, 'r')
            tfstate = fin.read()
            fin.close()
            return tfstate
        except Exception as e:
            # TODO: Catch the exception, or go ahead and fail?
            logging.debug('Reading state file failed. Using empty string.')
            return ''