import json
import flask
import unittest
import pyterrabacktyl

from CONSTS import C
from unittest import TestCase
from unittest.mock import patch
from abc_tylstore import TYLPersistent


class Test_pyterrabacktyl(TestCase):
    # def setUpClass(cls):
    #     pass

    def setUp(self):
        self.app = flask.Flask(__name__)
        with self.app.test_request_context('/?env=unittest'):
            # Force the creation of the object with 'unittest' as the environment name.
            pyterrabacktyl.set_env_from_url()


    @patch('pyterrabacktyl.request')
    def test_set_lock_state(self, mock_request):
        mock_request.method = C.HTTP_METHOD_LOCK
        mock_request.values = {'env': 'unittest'}
        mock_request.data = bytes(pyterrabacktyl._backends['unittest']._tflock, 'ascii')

        # Test locking from unlocked state.
        set_locked_value = pyterrabacktyl._set_lock_state(C.LOCK_STATE_LOCKED, [C.LOCK_STATE_UNLOCKED],
                                                          C.HTTP_METHOD_LOCK,
                                                          pyterrabacktyl._backends['unittest'].set_locked)
        self.assertEqual(set_locked_value, (pyterrabacktyl._backends['unittest']._tflock, C.HTTP_OK))

        # Test locking when someone else has lock.
        set_locked_value = pyterrabacktyl._set_lock_state(C.LOCK_STATE_LOCKED, [C.LOCK_STATE_UNLOCKED],
                                                          C.HTTP_METHOD_LOCK,
                                                          pyterrabacktyl._backends['unittest'].set_locked)
        self.assertEqual(set_locked_value, (pyterrabacktyl._backends['unittest']._tflock, C.HTTP_CONFLICT))

        # Test unlocking locked state
        mock_request.method = C.HTTP_METHOD_UNLOCK
        set_locked_value = pyterrabacktyl._set_lock_state(C.LOCK_STATE_UNLOCKED, [C.LOCK_STATE_LOCKED],
                                                          C.HTTP_METHOD_UNLOCK,
                                                          pyterrabacktyl._backends['unittest'].set_unlocked)
        self.assertEqual(set_locked_value, ('', C.HTTP_OK))

    @patch('pyterrabacktyl.request')
    def test_tf_lock(self, mock_request):
        mock_request.method = C.HTTP_METHOD_LOCK
        mock_request.values = {'env': 'unittest'}
        mock_request.data = bytes(pyterrabacktyl._backends['unittest']._tflock, 'ascii')

        self.assertEqual(pyterrabacktyl.tf_lock(), (pyterrabacktyl._backends['unittest']._tflock, C.HTTP_OK))

    @patch('pyterrabacktyl.request')
    def test_tf_unlock(self, mock_request):
        mock_request.method = C.HTTP_METHOD_UNLOCK
        mock_request.values = {'env': 'unittest'}
        mock_request.data = bytes(pyterrabacktyl._backends['unittest']._tflock, 'ascii')

        self.assertEqual(pyterrabacktyl.tf_unlock(), ('', C.HTTP_OK))

    @patch('pyterrabacktyl.request')
    def test_tf_backend(self, mock_request):
        mock_request.method = C.HTTP_METHOD_POST
        mock_request.values = {'env': 'unittest'}
        mock_request.data = bytes(pyterrabacktyl._backends['unittest']._tfstate, 'ascii')

        self.assertEqual(pyterrabacktyl.tf_backend(), ('alrighty!', C.HTTP_OK))

        mock_request.method = 'GET'
        self.assertEqual(pyterrabacktyl.tf_backend(), (pyterrabacktyl._backends['unittest']._tfstate, C.HTTP_OK))

    def test_service_state(self):
        # self.assertEqual(pyterrabacktyl.service_state(), 'moo')
        # TODO: There's tweaks that still need to be made to the output of this function, so can't assertEqual yet.
        ret_val = pyterrabacktyl.service_state()
        try:
            # Validate that we got something that can be converetd into json.
            json.loads(ret_val[0])
        except json.decoder.JSONDecodeError:
            self.fail('Expected to be able to parse string with json.loads()')
        self.assertEqual(ret_val[1], C.HTTP_OK)

    @patch('pyterrabacktyl.request')
    def test_shutdown(self, mock_request):
        mock_request.remote_addr = '10.10.10.10'
        self.assertEqual(pyterrabacktyl.shutdown(), ('', C.HTTP_UNAUTHORIZED))

        mock_request.remote_addr = '127.0.0.1'
        ret_val = pyterrabacktyl.shutdown()
        self.assertTrue(isinstance(int(ret_val[0]), int))
        self.assertEqual(ret_val[1], C.HTTP_OK)
        pyterrabacktyl._allow_lock = True

    def test_four_oh_four(self):
        self.assertEqual(pyterrabacktyl.four_oh_four('')[1], 404)

    @patch('pyterrabacktyl.request')
    def test_set_env_from_url(self, mock_request):
        mock_request.values = {'env': 'unittest'}
        pyterrabacktyl.set_env_from_url()
        self.assertEqual(pyterrabacktyl._env, 'unittest')
        self.assertTrue('unittest' in pyterrabacktyl._backends)
        self.assertTrue(isinstance(pyterrabacktyl._backends['unittest'], TYLPersistant))
        self.assertTrue('unittest' in pyterrabacktyl._post_processors)
        self.assertEqual(pyterrabacktyl._post_processors['unittest'], [])

    def test_load_class(self):
        obj_type = pyterrabacktyl._load_class('bogus_backend.BogusBackend', TYLPersistant)
        self.assertTrue(isinstance(obj_type(), TYLPersistant))

        self.assertRaises(pyterrabacktyl.PyTerraBackTYLException, pyterrabacktyl._load_class,
                          'bogus_backend.BogusBackend', int)


if __name__ == '__main__':
    unittest.main()
