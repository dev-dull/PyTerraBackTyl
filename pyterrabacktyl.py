import os
import sys
import json
import logging
import abc_tylstore

from CONSTS import C
from collections import Iterable
from flask import Flask, request
from importlib import import_module


class PyTerraBackTYLException(Exception):
    S_IS_INVALID_SUBCLASS_TYPE = '%s is invalid subclass type. Did you specify the subclass in your backend module?'
    S_IS_INVALID_LOCK_STATE = '%s is not a valid lock state.'
    LOCK_STATE_FOR_S_CHANGED_OUT_OF_PROCESS = 'Lock state for ENV %s appears to have been changed out-of-process!'


class PyTerraBackTYL(object):
    # Forcing flask into a class for no other reason than I want to avoid using the 'global' keyword.
    # This is likely and an area for improvement.
    def __init__(self):
        # TODO: thread-safe this variable
        self.__env = None
        self.__backends = {}
        self.__post_processors = {}
        self.backend_service = Flask('PyTerraBackTyl')
        self.backend_class = self.__load_class(C.BACKEND_CLASS, abc_tylstore.TYLPersistant)

        if C.POST_PROCESS_CLASSES:
            if isinstance(C.POST_PROCESS_CLASSES, str):
                C.POST_PROCESS_CLASSES = [C.POST_PROCESS_CLASSES]
            elif not isinstance(C.POST_PROCESS_CLASSES, Iterable):
                raise Exception('fuck')
        else:
            C.POST_PROCESS_CLASSES = []

        self.post_process_classes = [self.__load_class(c, abc_tylstore.TYLNonpersistant) for c in C.POST_PROCESS_CLASSES]

        def _set_lock_state(new_state, accepted_states, accepted_method, set_backend_state):
            self.set_env_from_url()
            if new_state in C.LOCK_STATES.keys():
                if request.method == accepted_method:
                    if self.__backends[self.__env].__lock_state__ in accepted_states:
                        old_state = self.__backends[self.__env].__lock_state__
                        self.__backends[self.__env].__lock_state__ = C.LOCK_STATE_INIT
                        if set_backend_state(request.data.decode()):
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
            state = _set_lock_state(C.LOCK_STATE_LOCKED, [C.LOCK_STATE_UNLOCKED],
                                    C.HTTP_METHOD_LOCK, self.__backends[self.__env].set_locked)

            # TODO: Process the plugins that are enabled, but not handling locking.
            for pp in self.__post_processors[self.__env]:
                try:
                    pp.on_locked(request.data.decode())
                except Exception as e:
                    logging.error(e)


            return state

        @self.backend_service.route('/unlock', methods=[C.HTTP_METHOD_UNLOCK, C.HTTP_METHOD_GET])
        def tf_unlock():
            state = _set_lock_state(C.LOCK_STATE_UNLOCKED, [C.LOCK_STATE_LOCKED, C.LOCK_STATE_INIT],
                                    C.HTTP_METHOD_UNLOCK, self.__backends[self.__env].set_unlocked)

            # TODO: Process the plugins that are enabled, but not handling locking.
            for pp in self.__post_processors[self.__env]:
                try:
                    pp.on_unlocked(request.data.decode())
                except Exception as e:
                    logging.error(e)

            return state

        @self.backend_service.route('/', methods=[C.HTTP_METHOD_GET, C.HTTP_METHOD_POST])
        def tf_backend():
            self.set_env_from_url()

            if request.method == 'POST':
                data = request.data.decode()
                self.__backends[self.__env].store_tfstate(data)
                logging.info('Stored new tfstate for ENV %s from IP %s.' % (self.__env, request.remote_addr))

                for pp in self.__post_processors[self.__env]:
                    try:
                        pp.process_tfstate(data)
                    except Exception as e:
                        logging.error(e)

                return 'alrighty!', C.HTTP_OK
            else:
                t = self.__backends[self.__env].get_tfstate()
                logging.info('Fetched tfstate for ENV %s from IP %s.' % (self.__env, request.remote_addr))
                return t, C.HTTP_OK

        @self.backend_service.route('/state', methods=['GET'])
        def service_state():
            # TODO: return legit values
            state = {'healthy': True,
                     'lock_state': self.__backends[self.__env].__lock_state__,
                     'http_code': C.LOCK_STATES[self.__backends[self.__env].__lock_state__],
                     'auth_service': C.USE_AUTHENTICATION_SERVICE}
            return json.dumps(state, indent=2)

        # TODO: Put some auth around forcing this to stop.
        # @self.backend_service.route('/shutdown')
        # def shutdown():
        #  Check if any repos are locked
        #  call the __backends.cleanup() functions
        #  bail out.
        #     func = request.environ.get('werkzeug.server.shutdown')
        #     if func is None:
        #         raise RuntimeError('Not running with the Werkzeug Server')
        #     func()
        #     return ''

        @self.backend_service.errorhandler(404)
        def four_oh_four(thing):
            return 'oh, snap. It done gone broked.', 404

    def set_env_from_url(self):
        # Looking at both GET and POST values.
        self.__env = request.values['env'] if 'env' in request.values else ''
        if self.__env not in self.__backends:
            self.__backends[self.__env] = self.backend_class(self.__env, C)
            self.__post_processors[self.__env] = [f(self.__env, C) for f in self.post_process_classes]

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
    logging.getLogger('').setLevel(getattr(logging, C.LOG_LEVEL.upper(), 'INFO'))
    PyTerraBackTYL().backend_service.run(host=C.BACKEND_SERVICE_IP, port=C.BACKEND_SERVICE_PORT)
