
from CONST_abated import load_from_yaml


# C is for CONST and that's good enough for me.
class C(object):
    ####################################################################################################################
    #
    #  ONLY SET VALUES HERE THAT SHOULD BE ALLOWED TO BE OVERRIDDEN IN consts.yaml
    #
    ####################################################################################################################

    # When false, use GitLab/Hub authentication???
    USE_AUTHENTICATION_SERVICE = True

    BACKEND_SERVICE_IP = '127.0.0.1'
    BACKEND_SERVICE_PORT = 2442
    AUTHENTICATION_SERVICE_PORT = 2443
    SSL_CERTIFICATE_PATH = '/SOME/PATH/TBD.key'  # TODO: http://flask.pocoo.org/snippets/111/

    BACKEND_PLUGINS_PATH = 'backends'
    BACKEND_CLASS = 'git_backend.GitBackend'

    LOG_LEVEL = 'INFO'

    # Declaring that these things exist so the IDE can find them without complaining. Values are populated below.
    AUTHENTICATION_SERVICE_IP = None

    HTTP_OK = None
    HTTP_LOCKED = None
    HTTP_CONFLICT = None
    HTTP_ERROR = None

    HTTP_METHOD_LOCK = None
    HTTP_METHOD_UNLOCK = None
    HTTP_METHOD_GET = None
    HTTP_METHOD_POST = None

    LOCK_STATE_INIT = None
    LOCK_STATE_LOCKED = None
    LOCK_STATE_UNLOCKED = None
    LOCK_STATES = None

    TFSTATE_FILE_NAME = None


# Override the constant values, set user specified constants.
load_from_yaml('config.yaml', C)


########################################################################################################################
#
#  Set values here that should NOT be allowed to be overridden in consts.yaml
#
########################################################################################################################
C.AUTHENTICATION_SERVICE_IP = '127.0.0.1'

C.HTTP_OK = 200
C.HTTP_LOCKED = 423
C.HTTP_CONFLICT = 409
C.HTTP_ERROR = 500

C.HTTP_METHOD_LOCK = 'LOCK'
C.HTTP_METHOD_UNLOCK = 'UNLOCK'
C.HTTP_METHOD_GET = 'GET'
C.HTTP_METHOD_POST = 'POST'

C.LOCK_STATE_INIT = 'INIT'
C.LOCK_STATE_LOCKED = 'LOCKED'
C.LOCK_STATE_UNLOCKED = 'UNLOCKED'
C.LOCK_STATES = {C.LOCK_STATE_INIT: C.HTTP_LOCKED,
                 C.LOCK_STATE_LOCKED: C.HTTP_CONFLICT,
                 C.LOCK_STATE_UNLOCKED: C.HTTP_OK}


C.TFSTATE_FILE_NAME = 'terraform.tfstate'

# If the user didn't manually specify a working directory, clean up the directory we crated in the OS's tmp space.
# TODO: Didn't work. Investigate or just rely on the OS doing this for us ... or do it as part of shutdown().
# import atexit
# @atexit.register
# def __cleanup():
#     if C.GIT_WORKING_PATH.startswith(tempfile.gettempdir()):
#         import shutil
#         shutil.rmtree(C.GIT_WORKING_PATH)
#         print('Removed:', C.GIT_WORKING_PATH)
