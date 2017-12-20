import os
import sys
import json
import ldap
import logging
import abc_tylstore

from CONSTS import C
from collections import Iterable
from flask import Flask, request
from importlib import import_module

__version__ = '1.0.0'


class PyTerraBackTYLException(Exception):
    S_IS_INVALID_SUBCLASS_TYPE = '%s is invalid subclass type. Did you specify the subclass in your backend module?'
    S_IS_INVALID_LOCK_STATE = '%s is not a valid lock state.'
    LOCK_STATE_FOR_S_CHANGED_OUT_OF_PROCESS = 'Lock state for ENV %s appears to have been changed out-of-process!'

    POST_PROCESSING_CLASS_SHOULD_BE_GOT_S = 'Expected list of strings for postprocessing class names. Got: %s'


# TODO: Pass 'self' to backends so they can add endpoints via self.backend_service
# TODO: When calling lock/unlock/store_state functions, parse the json in advance and also send raw_json

class PyTerraBackTYL(object):
    # Forcing flask into a class for no other reason than I want to avoid using the 'global' keyword.
    # This is likely and an area for improvement.
    def __init__(self):
        # TODO: thread-safe this variable
        self.__env = None
        self.__backends = {}
        self.__post_processors = {}
        self.__allow_lock = True
        self.backend_service = Flask('PyTerraBackTyl')
        self.backend_class = self.__load_class(C.BACKEND_CLASS, abc_tylstore.TYLPersistant)

        if C.POST_PROCESS_CLASSES:
            if isinstance(C.POST_PROCESS_CLASSES, str):
                C.POST_PROCESS_CLASSES = [C.POST_PROCESS_CLASSES]
            elif not isinstance(C.POST_PROCESS_CLASSES, Iterable):
                raise PyTerraBackTYLException(PyTerraBackTYLException.POST_PROCESSING_CLASS_SHOULD_BE_GOT_S % type(C.POST_PROCESS_CLASSES))
        else:
            C.POST_PROCESS_CLASSES = []

        self.post_process_classes = [self.__load_class(c, abc_tylstore.TYLNonpersistant) for c in C.POST_PROCESS_CLASSES]

        def _set_lock_state(new_state, accepted_states, accepted_method, set_backend_state):
            # TODO: `terraform force-unlock <ID>` doesn't work.
            self.set_env_from_url()
            if new_state in C.LOCK_STATES.keys():
                if request.method == accepted_method:
                    if self.__backends[self.__env].__lock_state__ in accepted_states:
                        old_state = self.__backends[self.__env].__lock_state__
                        self.__backends[self.__env].__lock_state__ = C.LOCK_STATE_INIT
                        lock_text = request.data.decode()
                        if set_backend_state(json.loads(lock_text), raw=lock_text):
                            logging.debug('Lock state set to %s' % new_state)
                            self.__backends[self.__env].__lock_state__ = new_state
                            return self.__backends[self.__env].get_lock_state(), C.HTTP_OK
                        self.__backends[self.__env].__lock_state__ = old_state  # maintain the old/bad state.
            # TODO: Lost connection during the last apply, race condition, or someone else changed state out-of-process.
            # TODO: Things are fucked up if the user got us here.
            lock_state = self.__backends[self.__env].get_lock_state()
            if lock_state:
                return lock_state, C.LOCK_STATES[C.LOCK_STATE_LOCKED]
            return 'I don\'t know, man. Something is really fucked up.',\
                   C.LOCK_STATES[self.__backends[self.__env].__lock_state__]

        @self.backend_service.route('/lock', methods=[C.HTTP_METHOD_LOCK, C.HTTP_METHOD_GET])
        def tf_lock():
            if self.__allow_lock:
                state = _set_lock_state(C.LOCK_STATE_LOCKED, [C.LOCK_STATE_UNLOCKED],
                                        C.HTTP_METHOD_LOCK, self.__backends[self.__env].set_locked)

                # TODO: This code block effectively exists in 3 places -- make it a function (1 of 3)
                # Process the nonpersistant plugins (enabled, but not handling locking).
                lock_text = request.data.decode()
                for pp in self.__post_processors[self.__env]:
                    try:
                        pp.on_locked(json.loads(lock_text), raw=lock_text)
                    except Exception as e:
                        pp.__logged_errors__ += 1
                        pp.__recent_error__ = str(e)
                        logging.error('%s: %s' % (pp.__class__.__name__, e))

                return state
            # Backend is shutting down. Return a 202 to say we got the request, but didn't do anything with it.
            return 'Backend service is shutting down.', C.HTTP_ACCEPTED

        @self.backend_service.route('/unlock', methods=[C.HTTP_METHOD_UNLOCK, C.HTTP_METHOD_GET])
        def tf_unlock():
            state = _set_lock_state(C.LOCK_STATE_UNLOCKED, [C.LOCK_STATE_LOCKED, C.LOCK_STATE_INIT],
                                    C.HTTP_METHOD_UNLOCK, self.__backends[self.__env].set_unlocked)

            # TODO: This code block effectively exists in 3 places -- make it a function (2 of 3)
            # Process the nonpersistant plugins (enabled, but not handling locking).
            lock_text = request.data.decode()
            for pp in self.__post_processors[self.__env]:
                try:
                    pp.on_unlocked(json.loads(lock_text), raw=lock_text)
                except Exception as e:
                    pp.__logged_errors__ += 1
                    pp.__recent_error__ = str(e)
                    logging.error('%s: %s' % (pp.__class__.__name__, e))

            return state

        @self.backend_service.route('/', methods=[C.HTTP_METHOD_GET, C.HTTP_METHOD_POST])
        def tf_backend():
            self.set_env_from_url()

            if request.method == 'POST':
                state_text = request.data.decode()
                state_obj = json.loads(state_text)
                self.__backends[self.__env].store_tfstate(state_obj, raw=state_text)
                logging.info('Stored new tfstate for ENV %s from IP %s.' % (self.__env, request.remote_addr))

                # TODO: This code block effectively exists in 3 places -- make it a function (3 of 3)
                # Process the nonpersistant plugins (enabled, but not handling locking).
                for pp in self.__post_processors[self.__env]:
                    try:
                        pp.process_tfstate(state_obj, raw=state_text)
                    except Exception as e:
                        pp.__logged_errors__ += 1
                        pp.__recent_error__ = str(e)
                        logging.error('%s: %s' % (pp.__class__.__name__, e))

                return 'alrighty!', C.HTTP_OK
            else:
                t = self.__backends[self.__env].get_tfstate()
                logging.info('Fetched tfstate for ENV %s from IP %s.' % (self.__env, request.remote_addr))
                return t, C.HTTP_OK

        @self.backend_service.route('/state', methods=['GET'])
        def service_state():
            state = {
                    C.TYL_KEYWORD_BACKEND_MODULE: C.BACKEND_CLASS,
                    C.TYL_KEYWORD_POST_PROCESSOR_MODULES: C.POST_PROCESS_CLASSES,
                    C.TYL_KEYWORD_BACKEND: {
                        C.TYL_KEYWORD_ENVIRONMENTS: []
                        },
                    C.TYL_KEYWORD_POST_PROCESSORS: []
                    }

            for env, backend in self.__backends.items():
                state[C.TYL_KEYWORD_BACKEND][C.TYL_KEYWORD_ENVIRONMENTS].append(
                    {
                        C.TYL_KEYWORD_ENVIRONMENT_NAME: env,
                        C.TYL_KEYWORD_LOCK_STATE: backend.__lock_state__,
                        C.TYL_KEYWORD_HTTP_STATE: C.LOCK_STATES[backend.__lock_state__],
                    }
                )

            for env, post_processor in self.__post_processors.items():
                for pp in post_processor:
                    state[C.TYL_KEYWORD_POST_PROCESSORS].append(
                        {env:
                             {
                                 pp.__class__.__name__:{
                                     C.TYL_KEYWORD_LOGGED_ERROR_CT: pp.__logged_errors__,
                                     C.TYL_KEYWORD_RECENT_LOGGED_ERROR: pp.__recent_error__,
                                 }
                             }
                        }
                )

            return json.dumps(state, indent=2), C.HTTP_OK

        # TODO: Put some auth around forcing this to stop.
        @self.backend_service.route('/getpid')
        def shutdown():
            if request.remote_addr == '127.0.0.1':
                self.__allow_lock = False
                for env, backend in self.__backends.items():
                    if backend.__lock_state__ in [C.LOCK_STATE_INIT, C.LOCK_STATE_LOCKED]:
                        self.__allow_lock = True
                        return 'False', C.HTTP_OK
                from os import getpid
                return str(getpid()), C.HTTP_OK
            return '', C.HTTP_UNAUTHORIZED

        @self.backend_service.errorhandler(404)
        def four_oh_four(thing):
            return 'oh, snap. It done gone broked.', 404

    def set_env_from_url(self):
        # Looking at both GET and POST values.
        self.__env = request.values['env'] if 'env' in request.values else ''
        if self.__env not in self.__backends:
            self.__backends[self.__env] = self.backend_class(self.__env, C, self)
            self.__post_processors[self.__env] = [c(self.__env, C, self) for c in self.post_process_classes]

    @staticmethod
    def __load_class(class_name, superclass):
        path_type = type(sys.path)  # Currently a list, but the Python overlords might change that some day.
        paths = path_type([os.sep.join(abc_tylstore.__file__.split(os.sep)[0:-1])])
        if isinstance(C.BACKEND_PLUGINS_PATH, str):
            C.BACKEND_PLUGINS_PATH = path_type([C.BACKEND_PLUGINS_PATH])
        else:
            C.BACKEND_PLUGINS_PATH = path_type(C.BACKEND_PLUGINS_PATH)
        paths += sys.path + C.BACKEND_PLUGINS_PATH
        sys.path = path_type(set(paths))

        # class_parts = C.BACKEND_CLASS.split('.')
        class_parts = class_name.split('.')
        _class = import_module(class_parts[0])
        for module_part in class_parts[1:]:
            logging.debug('Attempting to import: %s' % module_part)
            _class = getattr(_class, module_part)
        logging.debug('Successfully imported module %s' % class_name)

        if _class.__name__ in [sc.__name__ for sc in superclass.__subclasses__()]:
            logging.debug('Successful subclass type validation of %s' % C.BACKEND_CLASS)
            return _class
        else:
            logging.error(PyTerraBackTYLException.S_IS_INVALID_SUBCLASS_TYPE % C.BACKEND_CLASS)
            raise PyTerraBackTYLException(PyTerraBackTYLException.S_IS_INVALID_SUBCLASS_TYPE % C.BACKEND_CLASS)


if __name__ == '__main__':
    # TODO: This isn't the expected way to set up logging.
    logger = logging.getLogger('')
    logger.setLevel(getattr(logging, C.LOG_LEVEL.upper(), 'INFO'))
    logger.handlers[0].setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    PyTerraBackTYL().backend_service.run(host=C.BACKEND_SERVICE_IP, port=C.BACKEND_SERVICE_PORT)
