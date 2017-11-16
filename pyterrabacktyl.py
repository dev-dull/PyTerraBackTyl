import json
import logging
import argparse
from CONSTS import C
from flask import Flask, request

# mod=__import__('tyls')
# for mm in 'git_backend.GitBackend'.split('.'):
#    mod = getattr(mod, mm)
# mod('foo')


# LOCK STATE TO INIT
# GOT TFSTATE VIA request.data

# TODO: terraform uses the request methods LOCK, UNLOCK and POST. Is there value in going to a single endpoint?

class PyTerraBackTYL(object):
    # Forcing flask into a class for no other reason than I want to avoid using the 'global' keyword.
    # This is likely and an area for improvement.
    def __init__(self):
        # TODO: thread-safe this variable
        # TODO: make it a dict to track locking on multiple branches.
        self.__lock_state = C.LOCK_STATE_UNLOCKED
        self.backend_service = Flask('PyTerraBackTyl')

        def __just_testing():
            logging.debug('\n'.join(['%s: %s' % (k, v) for (k, v) in request.values.items()]) or 'No post/get datat to unpack')
            return '<br />'.join(['%s: %s' % (k, v) for (k, v) in request.values.items()])

        def __set_lock_state(state, method_ok, state_ok):
            print('%s:' % state.upper(), request.data)
            if state in C.LOCK_STATES.keys():
                if method_ok:
                    if state_ok:
                        self.__lock_state = state
                        logging.debug('Lock state set to %s' % state)
                        return 'State is now %s' % state, C.HTTP_OK
                    return 'Cannot change from state %s to %s' % (self.__lock_state, state), C.LOCK_STATES[self.__lock_state]
                return 'Invalid HTTP request method for state %s' % state, C.LOCK_STATES[self.__lock_state]
            else:
                raise Exception('Yo, goofball! That is not a lock state!')  # TODO: real error message, exception type.

        # TODO: decide how strict we should be with input methods
        @self.backend_service.route('/lock', methods=['LOCK', 'GET'])
        def tf_lock():
            __just_testing()
            return __set_lock_state(C.LOCK_STATE_INIT, request.method == C.HTTP_METHOD_LOCK,
                                    self.__lock_state == C.LOCK_STATE_UNLOCKED)

        @self.backend_service.route('/unlock', methods=['UNLOCK', 'GET'])
        def tf_unlock():
            __just_testing()
            return __set_lock_state(C.LOCK_STATE_UNLOCKED, request.method == C.HTTP_METHOD_UNLOCK,
                                    self.__lock_state in [C.LOCK_STATE_LOCKED, C.LOCK_STATE_INIT])

        @self.backend_service.route('/', methods=['GET', 'POST'])
        def tf_backend():
            fname = '/Users/alastad/wip/terraformPlayground/digitalocean/teststate'
            __just_testing()

            try:
                if request.method == 'POST':
                    t = request.data.decode()
                    fout = open(fname, 'w')
                    fout.write(t)
                    fout.close()
                    print('Files:', request.data)
                else:
                    fin = open(fname, 'r')
                    t = fin.read()
                    fin.close()
                return t, C.HTTP_OK
            except FileNotFoundError as e:
                return '', C.HTTP_OK

        @self.backend_service.route('/state', methods=['GET'])
        def healthcheck():
            # TODO: return legit values
            state = {'healthy': True,
                     'lock_state': self.__lock_state,
                     'http_code': C.LOCK_STATES[self.__lock_state],
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
            return 'oh, snap. It done gone broked.'


if __name__ == '__main__':
    logging.getLogger('').setLevel(logging.DEBUG)
    PyTerraBackTYL().backend_service.run(host=C.BACKEND_SERVICE_IP, port=C.BACKEND_SERVICE_PORT)
