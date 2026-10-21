"""Server test suite"""
import unittest
import json
import mock
import requests
import fmrest
from fmrest.exceptions import FileMakerError, BadJSON

URL = 'https://111.111.111.111'
ACCOUNT_NAME = 'demo'
ACCOUNT_PASS = 'demo'
DATABASE = 'Demo'
LAYOUT = 'Demo'

class ServerTestCase(unittest.TestCase):
    """Server test suite.

    Only put mocked requests here that don't need an actual FileMaker Server.
    """
    def setUp(self) -> None:

        # disable urlib warnings as we are testing with non verified certs
        requests.packages.urllib3.disable_warnings()

        self._fms = fmrest.Server(url=URL,
                                  user=ACCOUNT_NAME,
                                  password=ACCOUNT_PASS,
                                  database=DATABASE,
                                  layout=LAYOUT,
                                  api_version='v1'
                                 )

    @mock.patch.object(requests, 'request')
    def test_last_error(self, mock_request) -> None:
        """Test that FileMaker's errorCode response is available via last_error property."""
        mock_response = mock.Mock()
        mock_response.json.return_value = {'messages': [{'code': '212'}], 'response': {}}
        mock_request.return_value = mock_response

        # Error should be None when no request has been made yet
        self.assertEqual(self._fms.last_error, None)

        # Any FileMaker error code should raise a FileMakerError exception
        with self.assertRaises(FileMakerError):
            self._fms.login()

        # Assert last error to be error from mocked response
        self.assertEqual(self._fms.last_error, 212)

    @mock.patch.object(requests, 'request')
    def test_bad_json_response(self, mock_request) -> None:
        """Test handling of invalid JSON response."""
        mock_response = mock.Mock()
        mock_response.json.side_effect = json.decoder.JSONDecodeError('test', '', 0)
        mock_request.return_value = mock_response

        with self.assertRaises(BadJSON):
            self._fms.login()

    def test_non_ssl_handling(self) -> None:
        """Make sure you cannot instantiate a Server with an http address."""

        with self.assertRaises(ValueError):
            fmrest.Server(url="http://127.0.0.1",
                          user=ACCOUNT_NAME,
                          password=ACCOUNT_PASS,
                          database=DATABASE,
                          layout=LAYOUT,
                          api_version='v1'
                         )

    @mock.patch.object(requests, 'request')
    def test_auto_relogin_recovers_after_failed_relogin(self, mock_request) -> None:
        """Test that a failed re-login is retried on the next request instead of
        leaving the server without a token for good."""
        self._fms.auto_relogin = True

        def fms_response(code, response=None):
            mock_response = mock.Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'messages': [{'code': code}],
                                               'response': response or {}}
            return mock_response

        mock_request.side_effect = [
            fms_response('0', {'token': 'first'}),  # initial login
            fms_response('952'),                    # find: token expired
            requests.exceptions.ConnectionError(),  # re-login: server unreachable
            fms_response('0', {'token': 'second'}), # next find: pending re-login
            fms_response('0', {'data': []}),        # ... and the find itself
        ]

        self._fms.login()

        with self.assertRaises(fmrest.exceptions.RequestException):
            self._fms.find([{'name': 'test'}])
        self.assertIsNone(self._fms._token)

        self._fms.find([{'name': 'test'}])
        self.assertEqual(self._fms._token, 'second')
        last_headers = mock_request.call_args.kwargs['headers']
        self.assertEqual(last_headers['Authorization'], 'Bearer second')

    @mock.patch.object(requests, 'request')
    def test_auto_relogin_does_not_login_after_logout(self, mock_request) -> None:
        """Test that an explicit logout is not undone by auto_relogin."""
        self._fms.auto_relogin = True

        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'messages': [{'code': '0'}],
                                           'response': {'token': 'token'}}
        mock_request.return_value = mock_response

        self._fms.login()
        self._fms.logout()
        mock_request.reset_mock()

        self._fms.find([{'name': 'test'}])
        self.assertEqual(mock_request.call_count, 1)
        self.assertNotIn('/sessions', mock_request.call_args.kwargs['url'])
