import os
import sys
import json
import logging
import argparse
import abc_tylstore

from CONSTS import C
from functools import wraps
from flask import Flask, request
from importlib import import_module


class PyTerraBackTYL(object):
    # Forcing flask into a class for no other reason than I want to avoid using the 'global' keyword.
    # This is likely and an area for improvement.
    def __init__(self):
        # TODO: thread-safe this variable
        # TODO: make it a dict to track locking on multiple branches.
        self.__env = None
        self.__backends = {}
        self.backend_service = Flask('PyTerraBackTyl')

        path_type = type(sys.path)  # Currently a list, but the Python overlords might change that some day.
        paths = path_type([os.sep.join(abc_tylstore.__file__.split(os.sep)[0:-1])])
        if isinstance(C.BACKEND_PLUGINS_PATH, str):
            C.BACKEND_PLUGINS_PATH = path_type([C.BACKEND_PLUGINS_PATH])
        else:
            C.BACKEND_PLUGINS_PATH = path_type(C.BACKEND_PLUGINS_PATH)
        paths += sys.path + C.BACKEND_PLUGINS_PATH
        sys.path = path_type(set(paths))

        class_parts = C.BACKEND_CLASS.split('.')
        _class = import_module(class_parts[0])
        for module_part in class_parts[1:]:
            _class = getattr(_class, module_part)

        if _class.__name__ in [sc.__name__ for sc in abc_tylstore.TYLStore.__subclasses__()]:
            self.backend_class = _class
        else:
            raise Exception('FOOBARed!')

        def __just_testing():
            logging.debug('\n'.join(['%s: %s' % (k, v) for (k, v) in request.values.items()]) or 'No post/get datat to unpack')

        def __set_lock_state(state, method_ok, state_ok):
            print('%s:' % state.upper(), request.data)
            if state in C.LOCK_STATES.keys():
                if method_ok:
                    if state_ok:
                        self.__backends[self.__env].__lock_state__ = state
                        logging.debug('Lock state set to %s' % state)
                        return 'State is now %s' % state, C.HTTP_OK
                    return 'Cannot change from state %s to %s' % (self.__backends[self.__env].__lock_state__, state), C.LOCK_STATES[self.__backends[self.__env].__lock_state__]
                return 'Invalid HTTP request method for state %s' % state, C.LOCK_STATES[self.__backends[self.__env].__lock_state__]
            else:
                raise Exception('Yo, goofball! That is not a lock state!')  # TODO: real error message, exception type.

        @self.backend_service.route('/lock', methods=['LOCK', 'GET'])
        def tf_lock():
            self.set_env_from_url()
            __just_testing()
            lock_status = __set_lock_state(C.LOCK_STATE_INIT, request.method == C.HTTP_METHOD_LOCK,
                                           self.__backends[self.__env].__lock_state__ == C.LOCK_STATE_UNLOCKED)
            if self.__backends[self.__env].set_locked(request.data.decode()):
                self.__backends[self.__env].__lock_state__ = C.LOCK_STATE_LOCKED
                return lock_status
            return self.__backends[self.__env].get_lock_state(), C.HTTP_LOCKED

        @self.backend_service.route('/unlock', methods=['UNLOCK', 'GET'])
        def tf_unlock():
            self.set_env_from_url()
            __just_testing()
            lock_status = __set_lock_state(C.LOCK_STATE_UNLOCKED, request.method == C.HTTP_METHOD_UNLOCK,
                                           self.__backends[self.__env].__lock_state__ in [C.LOCK_STATE_LOCKED, C.LOCK_STATE_INIT])

            if self.__backends[self.__env].set_unlocked(request.data.decode()):
                return lock_status
            return 'Unlock failed.', C.HTTP_ERROR

        @self.backend_service.route('/', methods=['GET', 'POST'])
        def tf_backend():
            self.set_env_from_url()

            if request.method == 'POST':
                # TODO: decide if we really want to encode into utf-8
                self.__backends[self.__env].store_tfstate(request.data.decode())
                return 'alrighty!', C.HTTP_OK
            else:
                t = self.__backends[self.__env].get_tfstate()
                print('IS THIS WHERE WE ARE GETTING THE b CHARACTER?', t)
                return t, C.HTTP_OK

        @self.backend_service.route('/state', methods=['GET'])
        def state():
            # TODO: return legit values
            state = {'healthy': True,
                     'lock_state': self.__backends[self.__env].__lock_state__,
                     'http_code': C.LOCK_STATES[self.__backends[self.__env].__lock_state__],
                     'auth_service': C.USE_AUTHENTICATION_SERVICE}
            return json.dumps(state, indent=2)

        # TODO: Put some auth around forcing this to stop.
        # @self.backend_service.route('/shutdown')
        # def shutdown():
        #     func = request.environ.get('werkzeug.server.shutdown')
        #     if func is None:
        #         raise RuntimeError('Not running with the Werkzeug Server')
        #     func()
        #     return ''

        @self.backend_service.errorhandler(404)
        def four_oh_four(thing):
            print(request.url, thing)
            return 'oh, snap. It done gone broked.', 404

    def set_env_from_url(self):
        # TODO: currently looking at both GET and POST values. Maybe only GET makes sense here.
        self.__env = request.values['env'] if 'env' in request.values else ''
        if self.__env not in self.__backends:
            self.__backends[self.__env] = self.backend_class(self.__env)


if __name__ == '__main__':
    logging.getLogger('').setLevel(logging.DEBUG)
    PyTerraBackTYL().backend_service.run(host=C.BACKEND_SERVICE_IP, port=C.BACKEND_SERVICE_PORT)
