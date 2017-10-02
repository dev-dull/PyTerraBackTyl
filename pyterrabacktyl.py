import argparse
import json
from CONSTS import C
from flask import Flask

backend_service = Flask('PyTerraBackTyl')

# TODO: thread-safe this variable
__lock_state = C.LOCK_STATE_UNLOCKED

@backend_service.route('/lock')
def tf_lock():
    pass  # TODO

@backend_service.route('/unlock')
def tf_unlock():
    pass  # TODO

@backend_service.route('/')
def tf_backend():
    return 'Hello, World!'  # TODO

@backend_service.route('/healthcheck')
def _healthcheck():
    # TODO: return legit values
    state = {'healthy': True,
             'locked': __lock_state,
             'http_code': C.LOCK_STATES[__lock_state],
             'auth_service': C.USE_AUTHENTICATION_SERVICE}
    return json.dumps(state)

backend_service.run()
