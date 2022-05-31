from abc_tylstore import TYLPersistent


class BogusBackend(TYLPersistent):
    _pretend_to_be_locked = ""
    _tflock = (
        "{"
        '  "Operation": "OperationTypeApply",'
        '  "Version": "0.11.1",'
        '  "ID": "fb7f9374-c4b3-cc2c-c86f-a82879b36e80",'
        '  "Info": "",'
        '  "Path": "",'
        '  "Created": "2017-12-20T19:08:37.52413487Z",'
        '  "Who": "person@puter"'
        "}"
    )

    _tfstate = (
        "{"
        '    "version": 3,'
        '    "terraform_version": "0.11.1",'
        '    "serial": 2,'
        '    "lineage": "b69fd968-9b36-4105-b10a-8e1aff620d47",'
        '    "modules": ['
        "        {"
        '            "path": ['
        '                "root"'
        "            ],"
        '            "outputs": {},'
        '            "resources": {},'
        '            "depends_on": []'
        "        }"
        "    ]"
        "}"
    )

    def __init__(self, *args, **kwargs):
        pass

    def set_locked(self, state_obj, **kwargs):
        self._pretend_to_be_locked = self._tflock
        return True

    def set_unlocked(self, state_obj, **kwargs):
        self._pretend_to_be_locked = ""
        return True

    def get_lock_state(self):
        return self._pretend_to_be_locked

    def store_tfstate(self, tfstate_obj, **kwargs):
        pass

    def get_tfstate(self):
        return self._tfstate
