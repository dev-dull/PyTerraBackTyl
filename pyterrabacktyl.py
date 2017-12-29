import os
import sys
import json
import logging
import abc_tylstore

from CONSTS import C
from collections import Iterable
from flask import Flask, request
from importlib import import_module

__version__ = '1.1.4'
_env = None  # TODO: thread-safe this variable(?)
_backends = {}
_post_processors = {}
_allow_lock = True
backend_service = Flask('PyTerraBackTyl')


class PyTerraBackTYLException(Exception):
    S_IS_INVALID_SUBCLASS_TYPE = '%s is invalid subclass type. Did you specify the subclass in your backend module?'
    S_IS_INVALID_LOCK_STATE = '%s is not a valid lock state.'
    LOCK_STATE_FOR_S_CHANGED_OUT_OF_PROCESS = 'Lock state for ENV %s appears to have been changed out-of-process!'

    POST_PROCESSING_CLASS_SHOULD_BE_GOT_S = 'Expected list of strings for postprocessing class names. Got: %s'


if C.POST_PROCESS_CLASSES:
    if isinstance(C.POST_PROCESS_CLASSES, str):
        C.POST_PROCESS_CLASSES = [C.POST_PROCESS_CLASSES]
    elif not isinstance(C.POST_PROCESS_CLASSES, Iterable):
        raise PyTerraBackTYLException(PyTerraBackTYLException.POST_PROCESSING_CLASS_SHOULD_BE_GOT_S % type(C.POST_PROCESS_CLASSES))
else:
    C.POST_PROCESS_CLASSES = []


def _json_string(obj):
    return obj if isinstance(obj, str) else json.dumps(obj, indent=2)


def _set_lock_state(new_state, accepted_states, accepted_method, set_backend_state):
    # TODO: `terraform force-unlock <ID>` doesn't work.
    if new_state in C.LOCK_STATES.keys():
        if request.method == accepted_method:
            if _backends[_env].__lock_state__ in accepted_states:
                old_state = _backends[_env].__lock_state__
                _backends[_env].__lock_state__ = C.LOCK_STATE_INIT
                lock_text = request.data.decode() or '{}'
                if set_backend_state(json.loads(lock_text), raw=lock_text):
                    logging.debug('Lock state set to %s' % new_state)
                    _backends[_env].__lock_state__ = new_state
                    return _json_string(_backends[_env].get_lock_state()), C.HTTP_OK
                _backends[_env].__lock_state__ = old_state  # maintain the old/bad state.
    # TODO: Lost connection during the last apply, race condition, or someone else changed state out-of-process.
    # TODO: Things are fucked up if the user got us here.
    lock_state = _backends[_env].get_lock_state()
    if lock_state:
        return _json_string(lock_state), C.LOCK_STATES[C.LOCK_STATE_LOCKED]
    return 'I don\'t know, man. Something is really fucked up.',\
           C.LOCK_STATES[_backends[_env].__lock_state__]


@backend_service.route('/lock', methods=[C.HTTP_METHOD_LOCK, C.HTTP_METHOD_GET])
def tf_lock():
    set_env_from_url()
    if _allow_lock:
        state = _set_lock_state(C.LOCK_STATE_LOCKED, [C.LOCK_STATE_UNLOCKED],
                                C.HTTP_METHOD_LOCK, _backends[_env].set_locked)

        # TODO: This code block effectively exists in 3 places -- make it a function (1 of 3)
        # Process the nonpersistant plugins (enabled, but not handling locking).
        lock_text = request.data.decode()
        for pp in _post_processors[_env]:
            try:
                pp.on_locked(json.loads(lock_text), raw=lock_text)
            except Exception as e:
                pp.__logged_errors__ += 1
                pp.__recent_error__ = str(e)
                logging.error('%s: %s' % (pp.__class__.__name__, e))

        return state
    # Backend is shutting down. Return a 202 to say we got the request, but didn't do anything with it.
    return 'Backend service is shutting down.', C.HTTP_ACCEPTED


@backend_service.route('/unlock', methods=[C.HTTP_METHOD_UNLOCK, C.HTTP_METHOD_GET])
def tf_unlock():
    set_env_from_url()
    state = _set_lock_state(C.LOCK_STATE_UNLOCKED, [C.LOCK_STATE_LOCKED, C.LOCK_STATE_INIT],
                            C.HTTP_METHOD_UNLOCK, _backends[_env].set_unlocked)

    # TODO: This code block effectively exists in 3 places -- make it a function (2 of 3)
    # Process the nonpersistant plugins (enabled, but not handling locking).
    lock_text = request.data.decode()
    for pp in _post_processors[_env]:
        try:
            pp.on_unlocked(json.loads(lock_text), raw=lock_text)
        except Exception as e:
            pp.__logged_errors__ += 1
            pp.__recent_error__ = str(e)
            logging.error('%s: %s' % (pp.__class__.__name__, e))

    return state


@backend_service.route('/', methods=[C.HTTP_METHOD_GET, C.HTTP_METHOD_POST])
def tf_backend():
    set_env_from_url()

    if request.method == 'POST':
        state_text = request.data.decode()
        state_obj = json.loads(state_text)
        _backends[_env].store_tfstate(state_obj, raw=state_text)
        logging.info('Stored new tfstate for ENV %s from IP %s.' % (_env, request.remote_addr))

        # TODO: This code block effectively exists in 3 places -- make it a function (3 of 3)
        # Process the nonpersistant plugins (enabled, but not handling locking).
        for pp in _post_processors[_env]:
            try:
                pp.process_tfstate(state_obj, raw=state_text)
            except Exception as e:
                pp.__logged_errors__ += 1
                pp.__recent_error__ = str(e)
                logging.error('%s: %s' % (pp.__class__.__name__, e))

        return 'alrighty!', C.HTTP_OK
    else:
        t = _backends[_env].get_tfstate()
        logging.info('Fetched tfstate for ENV %s from IP %s.' % (_env, request.remote_addr))
        return _json_string(t), C.HTTP_OK


@backend_service.route('/state', methods=['GET'])
def service_state():
    state = {
            C.TYL_KEYWORD_BACKEND_MODULE: C.BACKEND_CLASS,
            C.TYL_KEYWORD_POST_PROCESSOR_MODULES: C.POST_PROCESS_CLASSES,
            C.TYL_KEYWORD_BACKEND: {
                C.TYL_KEYWORD_ENVIRONMENTS: []
                },
            C.TYL_KEYWORD_POST_PROCESSORS: []
            }

    for env, backend in _backends.items():
        state[C.TYL_KEYWORD_BACKEND][C.TYL_KEYWORD_ENVIRONMENTS].append(
            {
                C.TYL_KEYWORD_ENVIRONMENT_NAME: env,
                C.TYL_KEYWORD_LOCK_STATE: backend.__lock_state__,
                C.TYL_KEYWORD_HTTP_STATE: C.LOCK_STATES[backend.__lock_state__],
            }
        )

    for env, post_processor in _post_processors.items():
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
@backend_service.route('/getpid')
def shutdown():
    global _allow_lock
    if request.remote_addr == '127.0.0.1':
        _allow_lock = False
        for env, backend in _backends.items():
            if backend.__lock_state__ in [C.LOCK_STATE_INIT, C.LOCK_STATE_LOCKED]:
                _allow_lock = True
                return 'False', C.HTTP_OK
        from os import getpid
        return str(getpid()), C.HTTP_OK
    return '', C.HTTP_UNAUTHORIZED


@backend_service.errorhandler(404)
def four_oh_four(thing):
    return 'oh, snap. It done gone broked.', 404


def set_env_from_url():
    # Looking at both GET and POST values.
    global _env
    _env = request.values['env'] if 'env' in request.values else ''
    if _env not in _backends:
        _backends[_env] = backend_class(_env, C, backend_service)
        _post_processors[_env] = [c(_env, C, backend_service) for c in post_process_classes]

        if _backends[_env].get_lock_state():
            _backends[_env].__lock_state__ = C.LOCK_STATE_LOCKED


def _load_class(class_name, superclass):
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


backend_class = _load_class(C.BACKEND_CLASS, abc_tylstore.TYLPersistant)
post_process_classes = [_load_class(c, abc_tylstore.TYLNonpersistant) for c in C.POST_PROCESS_CLASSES]

if __name__ == '__main__':
    # TODO: This isn't the expected way to set up logging.
    logger = logging.getLogger('')
    logger.setLevel(getattr(logging, C.LOG_LEVEL.upper(), 'INFO'))
    logger.handlers[0].setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    # PyTerraBackTYL().\
    backend_service.run(host=C.BACKEND_SERVICE_IP, port=C.BACKEND_SERVICE_PORT)
