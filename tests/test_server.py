"""Server test suite"""
import os
import unittest
import json
import mock
import requests
import fmrest

# Settings for fmrest test database
# (if you want to change credentials when hosting the test db, please use the env vars to do so)
URL = os.getenv('URL', 'https://10.211.55.15')
ACCOUNT_NAME = os.getenv('ACCOUNT_NAME', 'admin')
ACCOUNT_PASS = os.getenv('ACCOUNT_PASS', 'admin')
DATABASE = os.getenv('DATABASE', 'fmwrapper')
LAYOUT = os.getenv('LAYOUT', 'Contacts')

class ServerTestCase(unittest.TestCase):
    """Server test suite"""
    def setUp(self):

        # disable urlib warnings as we are testing with non verified certs
        requests.packages.urllib3.disable_warnings()

        self._fms = fmrest.Server(url=URL,
                                  user=ACCOUNT_NAME,
                                  password=ACCOUNT_PASS,
                                  database=DATABASE,
                                  layout=LAYOUT,
                                  verify_ssl=False
                                 )
    def test_login(self):
        """Test that login returns string token on success."""
        self.assertIsInstance(self._fms.login(), str)

    def test_logout(self):
        pass

    def test_delete_record(self):
        pass

    def test_create_record(self):
        pass

    def test_get_records(self):
        pass

    def test_get_record(self):
        """Test that get_record returns a Record instance"""
        with self._fms as server:
            server.login()
            self.assertIsInstance(self._fms.get_record(2), fmrest.record.Record)

    def test_non_ssl_handling(self):
        """Test that non-SSL call raises a FileMakerError exception

        FileMaker Server returns no errorCode in this case, but only an error message
        """

        self._fms.url = self._fms.url.replace('https:', 'http:')
        with self.assertRaises(fmrest.exceptions.FileMakerError):
            self._fms.login()

    # --------------
    # Mocked requests
    # --------------

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
