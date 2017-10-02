from CONST_abated import load_from_yaml


# C is for CONST and that's good enough for me.
class C(object):
    ####################################################################################################################
    #
    #  ONLY SET VALUES HERE THAT SHOULD BE ALLOWED TO BE OVERRIDDEN IN consts.yaml
    #
    ####################################################################################################################
    GIT_REPOSITORY = None
    GIT_KEY_FILE = '~/.ssh/id_rsa'
    GIT_USERNAME: None
    GIT_PASSWORD: None

    USE_AUTHENTICATION_SERVICE = True

    BACKEND_SERVICE_IP = '127.0.0.1'
    BACKEND_SERVICE_PORT = 2442
    AUTHENTICATION_SERVICE_PORT = 2443

    # Declaring that these things exist so the IDE can find them without complaining. Values are populated below.
    AUTHENTICATION_SERVICE_IP = None

    HTTP_STATE_LOCKED = None
    HTTP_STATE_CONFLICT = None
    HTTP_STATE_UNLOCKED = None

    LOCK_STATE_INIT = None
    LOCK_STATE_LOCKED = None
    LOCK_STATE_UNLOCKED = None
    LOCK_STATES = None

# Override the constant values, set user specified constants.
load_from_yaml('consts.yaml', C)

########################################################################################################################
#
#  Set values here that should NOT be allowed to be overridden in consts.yaml
#
########################################################################################################################
C.AUTHENTICATION_SERVICE_IP = '127.0.0.1'

C.HTTP_STATE_LOCKED = 423
C.HTTP_STATE_CONFLICT = 409
C.HTTP_STATE_UNLOCKED = 200

C.LOCK_STATE_INIT = 'INIT'
C.LOCK_STATE_LOCKED = 'LOCKED'
C.LOCK_STATE_UNLOCKED = 'UNLOCKED'
C.LOCK_STATES = {C.LOCK_STATE_INIT: C.HTTP_STATE_LOCKED,
                 C.LOCK_STATE_LOCKED: C.HTTP_STATE_CONFLICT,
                 C.LOCK_STATE_UNLOCKED: C.HTTP_STATE_UNLOCKED}