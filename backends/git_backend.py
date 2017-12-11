import os
import git
import json
import logging
import tempfile

from collections import defaultdict
from abc_tylstore import TYLPersistant


class GitBackend(TYLPersistant):
    def __init__(self, environment, constants):
        self.new_branch = False
        self.C = constants
        self.ENV = environment if environment else self.C.GIT_DEFAULT_CLONE_BRANCH.split('/')[-1]
        self.push_origin = self.C.GIT_DEFAULT_CLONE_BRANCH.split('/')[0]

        # I don't like keeping this here, but this info isn't sent with the current tfstate
        # and I want to keep the commit messages relevant to who has the current lock.
        self.lock_commit_msg = ''

        # The calls to tempfile.mkdtemp() looks redundant here, but this handles the cases where
        # GIT_WORKING_PATH is None or not configured.
        self.working_dir = getattr(self.C, 'GIT_WORKING_PATH', tempfile.mkdtemp()) or tempfile.mkdtemp()
        if self.working_dir.endswith(os.sep):
            self.working_dir = self.working_dir[0:-1]
        self.working_dir = os.sep.join([self.working_dir, self.ENV])
        self.tfstate_file_name = os.sep.join([self.working_dir, self.C.TFSTATE_FILE_NAME])
        self.lockfile = os.sep.join([self.working_dir, self.C.LOCK_STATE_LOCKED])
        self.logfile = os.sep.join([self.working_dir, self.C.GIT_STATE_CHANGE_LOG_FILENAME])

        self.repository = git.Git(self.working_dir)
        logging.info('Git working directory for ENV %s: %s ' % (self.ENV, self.working_dir))
        self.__make_repo()

    def __make_repo(self):
        if not os.path.exists(self.working_dir):
            # TODO: Let the user config the directory permissions.
            # Hairy because str(?) -> octal int is prone to human error.
            os.mkdir(self.working_dir, mode=0o750)
            self.repository.clone(self.C.GIT_REPOSITORY, self.working_dir)
            logging.info('Cloned %s for ENV %s to directory %s' % (self.C.GIT_REPOSITORY, self.ENV, self.working_dir))

        # TODO: Yuck. Why doesn't GitPython do this for me?
        branches = [b.split('-')[0].split('/')[-1].strip() for b in self.repository.branch('-r').splitlines()]
        if self.ENV in branches:
            self.repository.checkout(self.ENV)
            logging.debug('Checked out existing branch %s' % self.ENV)
        else:
            self.new_branch = True
            self.repository.checkout(self.C.GIT_DEFAULT_CLONE_BRANCH, b=self.ENV)
            logging.info('Created new branch %s.' % self.ENV)
        self.repository.pull()
        self.repository.branch(d='master')  # Delete the LOCAL copy of the 'master' branch
                                            # Hopefully this'll surppress 'X commits of head of master' warnings.

    def set_locked(self, request):
        # TODO: if the commit/push fails (e.g. because the user.name and user.email vaules weren't set) then we'll appear to be in a locked state when we're not

        self.repository.pull()

        if os.path.exists(self.lockfile):
            logging.warning('Failed to obtain lock for ENV %s, already locked: %s' % (self.ENV, self.lockfile))
            return False

        logging.info('Locking ENV %s: file is %s' % (self.ENV, self.lockfile))
        fout = open(self.lockfile, 'w')
        json_obj = json.loads(request)
        fout.write(json.dumps(json_obj, indent=2))
        fout.close()
        del fout

        self._update_log(json_obj)
        self.repository.add([self.lockfile, self.logfile])
        self.lock_commit_msg = self.C.GIT_COMMIT_MESSAGE_FORMAT.format(**defaultdict(str, json_obj))
        self.repository.commit(m=self.lock_commit_msg or 'FORCED CHANGE')
        self.repository.push(self.push_origin, self.ENV)
        # write request.data to file
        # commit/push lock file
        return True

    def set_unlocked(self, request):
        self.repository.pull()
        if os.path.exists(self.lockfile):
            json_obj = json.loads(request)
            self._update_log(json_obj)
            self.repository.rm(self.lockfile)
            self.repository.add(self.logfile)
            # Using defaultdict here will give us an empty string for any invalid format values configured by the user.
            self.repository.commit(m=self.C.GIT_COMMIT_MESSAGE_FORMAT.format(**defaultdict(str, json_obj)))
            self.repository.push(self.push_origin, self.ENV)
            return True
        logging.warning('Failed to release lock for ENV %s, already unlocked!' % self.ENV)
        return False

    def _update_log(self, json_obj):
        try:
            scrollback = -1 * abs(int(self.C.GIT_STATE_CHANGE_LOG_SCROLLBACK))
        except ValueError:
            logging.error('Scrollback value %s is not an integer. Using 300.' % self.C.GIT_STATE_CHANGE_LOG_SCROLLBACK)
            scrollback = 300

        if os.path.exists(self.logfile):
            foutin = open(self.logfile, 'r+')
            log_lines = foutin.read().splitlines()[scrollback:]
            foutin.seek(0)
        else:
            foutin = open(self.logfile, 'w')
            log_lines = []

        foutin.seek(0)
        # Using defaultdict here will give us an empty string for any invalid format values configured by the user.
        log_lines.append(self.C.GIT_STATE_CHANGE_LOG_FORMAT.format(**defaultdict(str, json_obj)))
        foutin.write('\n'.join(log_lines) + '\n')
        foutin.close()
        del foutin

    def get_lock_state(self):
        self.repository.pull()
        if os.path.exists(self.lockfile):
            fin = open(self.lockfile, 'r')
            state = fin.read()
            fin.close()
            logging.debug('Returning locked state %s' % state)
            return state
        return ''

    def store_tfstate(self, tfstate_text):
        self.repository.pull()

        backup_file = self.tfstate_file_name+'.backup'
        commit_files = [self.tfstate_file_name]
        if os.path.exists(self.tfstate_file_name):
            logging.debug('Renaming existing tfstate from %s to %s' % (self.lockfile, backup_file))
            os.rename(self.tfstate_file_name, backup_file)
            commit_files.append(backup_file)
        fout = open(self.tfstate_file_name, 'w')
        fout.write(tfstate_text)
        fout.close()

        self.repository.add(commit_files)
        self.repository.commit(m=self.lock_commit_msg)
        self.repository.push(self.push_origin, self.ENV)

        logging.debug('Saved state file %s' % self.tfstate_file_name)

    def get_tfstate(self):
        self.repository.pull()

        try:
            logging.debug('Reading state file %s' % self.tfstate_file_name)
            fin = open(self.tfstate_file_name, 'r')
            tfstate = fin.read()
            fin.close()
            return tfstate
        except Exception as e:
            if self.new_branch:
                logging.info('Reading state file failed. "%s" appears to be a new ENV. Using empty string.' % self.ENV)
                return ''
            raise e
