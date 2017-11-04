"""Server test suite"""
import os
import unittest
import requests
import fmrest
from fmrest.record import Record

# Settings for fmrest test database 'Contacts'
# Running theses tests requires you to have a FileMaker Server running
# (if you want to change credentials when hosting the test db, please use the env vars to do so)
URL = os.getenv('URL', 'https://10.211.55.15')
ACCOUNT_NAME = os.getenv('ACCOUNT_NAME', 'admin')
ACCOUNT_PASS = os.getenv('ACCOUNT_PASS', 'admin')
DATABASE = os.getenv('DATABASE', 'Contacts')
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
        with self._fms as server:
            self.assertIsInstance(server.login(), str)

    def test_logout(self):
        """Test that server accepts logout request."""
        self._fms.login()
        self.assertTrue(self._fms.logout())

    def test_create_get_delete_record(self):
        """Create a record, get it, delete it. Assert all steps work in succession."""
        with self._fms as server:
            server.login()

            #create a test record and get its ID
            record_id = server.create_record({'name': 'FileMaker サーバ', 'date': '04.11.2017'})
            self.assertIsInstance(record_id, int)

            #read the new record and compare the written value
            record = server.get_record(record_id)
            self.assertEqual(record.record_id(), record_id)
            self.assertEqual(record.name, 'FileMaker サーバ')

            #delete record by the ID
            deleted = server.delete_record(record_id)
            self.assertTrue(deleted)

    def test_get_records(self):
        pass

    def test_find(self):
        pass

    def test_edit_record(self):
        pass

    def test_set_globals_to_access_related_values(self):
        """Test that we can set a global value in the current session and then
        use it to access a related value
        """

        with self._fms as server:
            server.login()

            # give the global field the value of an existing note record
            globals_ = {'g_note_id_active': '1'}
            set_globals = server.set_globals(globals_)
            self.assertTrue(set_globals)

            # now request a record and check that the relationship using this global
            # field can be established.
            record = server.get_record(3) # can be any, as we use a global relationship
            self.assertEqual(
                record['Notes_active::note'], 'This is a test note. Do not delete or change.'
            )

    def test_get_record(self):
        """Test that get_record returns the Record value we are expecting."""
        with self._fms as server:
            server.login()
            fake_record = Record(['name', 'drink'], ['Do not delete record 1', 'Coffee'])
            record = server.get_record(1)
            self.assertEqual(fake_record.name, record.name)
            self.assertEqual(fake_record.drink, record.drink)

    def test_non_ssl_handling(self):
        """Test that non-SSL call raises a FileMakerError exception

        FileMaker Server returns no errorCode in this case, but only an error message
        """

        self._fms.url = self._fms.url.replace('https:', 'http:')
        with self.assertRaises(fmrest.exceptions.FileMakerError):
            self._fms.login()
