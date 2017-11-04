"""Server test suite"""
import unittest
import json
import mock
import requests
import fmrest

URL = 'https://111.111.111.111'
ACCOUNT_NAME = 'demo'
ACCOUNT_PASS = 'demo'
DATABASE = 'Demo'
LAYOUT = 'Demo'

class ServerTestCase(unittest.TestCase):
    """Server test suite.

    Only put mocked requests here that don't need an actual FileMaker Server.
    """
    def setUp(self):

        # disable urlib warnings as we are testing with non verified certs
        requests.packages.urllib3.disable_warnings()

        self._fms = fmrest.Server(url=URL,
                                  user=ACCOUNT_NAME,
                                  password=ACCOUNT_PASS,
                                  database=DATABASE,
                                  layout=LAYOUT
                                 )

    @mock.patch.object(requests, 'request')
    def test_last_error(self, mock_request):
        """Test that FileMaker's errorCode response is available via last_error property."""
        mock_response = mock.Mock()
        mock_response.json.return_value = {"errorCode": "212"}
        mock_request.return_value = mock_response

        # Error should be None when no request has been made yet
        self.assertEqual(self._fms.last_error, None)

        # Any FileMaker "errorCode" should raise a FileMakerError exception
        with self.assertRaises(fmrest.exceptions.FileMakerError):
            self._fms.login()

        # Assert last error to be error from mocked response
        self.assertEqual(self._fms.last_error, 212)

    @mock.patch.object(requests, 'request')
    def test_bad_json_response(self, mock_request):
        """Test handling of invalid JSON response."""
        mock_response = mock.Mock()
        mock_response.json.side_effect = json.decoder.JSONDecodeError('test', '', 0)
        mock_request.return_value = mock_response

        with self.assertRaises(fmrest.exceptions.BadJSON):
            self._fms.login()
