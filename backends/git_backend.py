import os
import git
import json
import logging
import tempfile
from CONSTS import C
from abc_tylstore import TYLStore


class GitBackend(TYLStore):
    def __init__(self, environment):
        self.ENV = environment

        self.working_dir = C.GIT_WORKING_PATH or tempfile.mkdtemp()
        if self.working_dir.endswith(os.sep):
            self.working_dir = self.working_dir[0:-1]
        self.working_dir = os.sep.join([self.working_dir, self.ENV])
        self.tfstate_file_name = os.sep.join([self.working_dir, C.TFSTATE_FILE_NAME])
        self.lockfile = os.sep.join([self.working_dir, 'LOCKED'])

        self.repository = git.Git(self.working_dir)
        logging.debug('zjfdsklfjslkdfjlasdkjflaskdjflaksdjflasd '+self.working_dir)
        self.__make_repo()

    def __make_repo(self):
        if not os.path.exists(self.working_dir):
            os.mkdir(self.working_dir, mode=0o700)
            self.repository.clone(C.GIT_REPOSITORY, self.working_dir)

        # TODO: Yuck. Why doesn't GitPython do this for me?
        branches = [b.split('-')[0].split('/')[-1] for b in self.repository.branch('-r').replace('\r', '').split('\n')]
        if self.ENV in branches:
            self.repository.checkout(self.ENV)
        else:
            self.repository.checkout('origin/master', b=self.ENV)
        self.repository.pull()

    def set_locked(self, request):
        # create lock file
        logging.debug('LOCK file is %s' % self.lockfile)

        self.repository.pull()

        if os.path.exists(self.lockfile):
            return False

        fout = open(self.lockfile, 'w')
        fout.write(json.dumps(json.loads(request), indent=2))
        fout.close()
        self.repository.add(self.lockfile)
        self.repository.commit(m='How locked? Land locked!')
        self.repository.push('origin', self.ENV)
        # write request.data to file
        # commit/push lock file
        return True

    def set_unlocked(self, request):
        self.repository.pull()
        if os.path.exists(self.lockfile):
            self.repository.rm(self.lockfile)
            self.repository.commit(m='Remove lock file')
            self.repository.push('origin', self.ENV)
            return True
        return False

    def get_lock_state(self):
        self.repository.pull()
        if os.path.exists(self.lockfile):
            fin = open(self.lockfile, 'r')
            state = fin.read()
            fin.close()
            logging.debug('STATE: %s' % state)
            return state
        return None

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