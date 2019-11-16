"""Server test suite"""
import os
import unittest
import requests
import fmrest
import json
from fmrest.record import Record
from fmrest.exceptions import RecordError

# Settings for fmrest test database 'Contacts'
# Running theses tests requires you to have a FileMaker Server running
# (if you want to change credentials when hosting the test db, please use the env vars to do so)
URL = os.getenv('URL', 'https://macvm2.local')
ACCOUNT_NAME = os.getenv('ACCOUNT_NAME', 'admin')
ACCOUNT_PASS = os.getenv('ACCOUNT_PASS', 'admin')
DATABASE = os.getenv('DATABASE', 'Contacts')
LAYOUT = os.getenv('LAYOUT', 'Contacts')
VERIFY_SSL = os.getenv('VERIFY_SSL', os.path.dirname(os.path.realpath(__file__)) + '/CA.pem')

SECOND_DS = os.getenv('SECOND_DS', 'secondDataSource')
SECOND_DS_ACCOUNT_NAME = os.getenv('SECOND_DS_ACCOUNT_NAME', 'admin2')
SECOND_DS_ACCOUNT_PASS = os.getenv('SECOND_DS_ACCOUNT_PASS', 'admin2')

class ServerTestCase(unittest.TestCase):
    """Server test suite"""
    def setUp(self) -> None:

        # disable urlib warnings as we are testing with non verified certs
        requests.packages.urllib3.disable_warnings()

        self._fms = fmrest.Server(url=URL,
                                  user=ACCOUNT_NAME,
                                  password=ACCOUNT_PASS,
                                  database=DATABASE,
                                  layout=LAYOUT,
                                  verify_ssl=VERIFY_SSL
                                 )
    def test_login(self) -> None:
        """Test that login returns string token on success."""
        with self._fms as server:
            self.assertIsInstance(server.login(), str)

    def test_login_data_sources(self):
        """Test login with second data source."""
        fms = fmrest.Server(url=URL,
                            user=ACCOUNT_NAME,
                            password=ACCOUNT_PASS,
                            database=DATABASE,
                            layout=LAYOUT,
                            verify_ssl=VERIFY_SSL,
                            data_sources=[
                                {'database': SECOND_DS,
                                 'username': SECOND_DS_ACCOUNT_NAME,
                                 'password': SECOND_DS_ACCOUNT_PASS}
                            ]
                           )
        with fms as server:
            server.login()
            record = server.get_record(1, portals=[{'name': 'secondDataSource'}])
            # read test value from second data source
            self.assertEqual(record.portal_secondDataSource[0]['secondDataSource::id'], 1)

    def test_logout(self) -> None:
        """Test that server accepts logout request."""
        self._fms.login()
        self.assertTrue(self._fms.logout())

    def test_create_get_delete_record(self) -> None:
        """Create a record, get it, delete it. Assert all steps work in succession."""
        with self._fms as server:
            server.login()

            #create a test record and get its ID
            record_id = server.create_record({'name': 'FileMaker サーバ', 'date': '04.11.2017'})
            self.assertIsInstance(record_id, int)

            #read the new record and compare the written value
            record = server.get_record(record_id)
            self.assertEqual(record.record_id, record_id)
            self.assertEqual(record.name, 'FileMaker サーバ')

            #delete record by the ID
            deleted = server.delete_record(record_id)
            self.assertTrue(deleted)

    def test_create_record_from_record_instance(self) -> None:
        """Create a record from a new record instance."""

        record = Record(['name', 'drink'], ['David', 'Coffee'])

        with self._fms as server:
            server.login()
            record_id = server.create(record)

        self.assertIsInstance(record_id, int)

    def test_info(self) -> None:
        """Test that foundset info property contains data as expected.

        The executed script computes the expected information independently and is used to
        make a comparision against the data computed by the FMDAPI"""
        with self._fms as server:
            server.login()
            foundset = server.find(query=[{'id': 1}], scripts={'after': ['testScript_dataInfo', None]})
            expected_info = json.loads(server.last_script_result['after'][1])

        self.assertDictEqual(foundset.info, expected_info['general'])
        self.assertDictEqual(foundset[0].portal_notes.info, expected_info['portal_notes'])

    def test_get_records(self):
        # TODO
        pass

    def test_find(self):
        # TODO
        pass

    def test_edit_record(self):
        # TODO
        pass

    def test_perform_script_single(self) -> None:
        """Perform script via dedicated script route introduced in FMS18"""
        param = 'input'
        expected_script_result = 'Output with param ' + param
        expected_return = (0, expected_script_result)

        with self._fms as server:
            server.login()
            ps_res = server.perform_script('testScript', param)
            ps_last_result = server.last_script_result

        self.assertEqual(ps_res, expected_return)

        # also check that last_script_result was updated
        self.assertEqual(ps_last_result, {'after': [0, expected_script_result]})

    def test_perform_script_single_with_error(self) -> None:
        """Perform script w/ error via dedicated script route introduced in FMS18"""
        expected_return = (3, None)

        with self._fms as server:
            server.login()
            ps_res = server.perform_script('testScriptWithError')
            ps_last_result = server.last_script_result

        self.assertEqual(ps_res, expected_return)

        # also check that last_script_result was updated
        self.assertEqual(ps_last_result, {'after': [3, None]})

    def test_perform_scripts_with_find(self) -> None:
        """Perform scripts for find route and verify results."""
        expected_script_result = {
            'prerequest': [0, 'Output prerequest with param for prerequest'],
            'presort': [0, 'Output presort with param for presort'],
            'after': [0, 'Output with param for after'],
        }
        with self._fms as server:
            server.login()
            server.find(
                query=[{'id': '1'}],
                scripts={
                    'prerequest': ['testScript_prerequest', 'for prerequest'],
                    'presort': ['testScript_presort', 'for presort'],
                    'after': ['testScript', 'for after'],
                })

            self.assertEqual(server.last_script_result, expected_script_result)

    def test_perform_script_find_with_error(self) -> None:
        """Perform a script via find route that contains an error and check if error is returned."""
        expected_script_result = {'after': [3, None]} # unsupported script step

        with self._fms as server:
            server.login()
            server.find(
                query=[{'id': '1'}],
                scripts={'after': ['testScriptWithError', None]})

            self.assertEqual(server.last_script_result, expected_script_result)

    def test_delete_record_instance(self) -> None:
        with self._fms as server:
            server.login()

            # create dummy record
            record = Record(['name'], ['David'])
            new_record_id = server.create(record)

            # "hand-made" record not fetched from server should fail for deletion
            with self.assertRaises(RecordError):
                server.delete(record)

            # fetch record from server so that we have a valid record instance
            record = server.get_record(new_record_id)

            # test deletion
            deletion_result = server.delete(record)
            self.assertTrue(deletion_result)

    def test_duplicate_by_get_create(self) -> None:
        """Test that we can pass a record instance from get_record directly to create().

        Note that this might not be a practical application in real life, as duplicating
        a record like this will only work if you have no ID fields, calc fields, etc. in your
        record instance.
        """

        with self._fms as server:
            server.layout = 'Planets' # different test layout with no IDs / calcs
            server.login()
            record = server.get_record(5)

            # duplicate record by passing rec instance to create method
            duplicated_record_id = server.create(record)
            self.assertIsInstance(duplicated_record_id, int)

            # delete test record
            server.delete_record(duplicated_record_id)

    def test_set_globals_to_access_related_values(self) -> None:
        """Test that we can set a global value in the current session and then
        use it to access a related value
        """

        with self._fms as server:
            server.login()

            # give the global field the value of an existing note record
            globals_ = {'Contacts::g_note_id_active': '1'}
            set_globals = server.set_globals(globals_)
            self.assertTrue(set_globals)

            # now request a record and check that the relationship using this global
            # field can be established.
            record = server.get_record(497) # can be any, as we use a global relationship
            self.assertEqual(
                record['Notes_active::note'], 'This is a test note. Do not delete or change.'
            )

    def test_get_record(self) -> None:
        """Test that get_record returns the Record value we are expecting."""
        with self._fms as server:
            server.login()
            fake_record = Record(['name', 'drink'], ['Do not delete record 1', 'Coffee'])
            record = server.get_record(1)
            self.assertEqual(fake_record.name, record.name)
            self.assertEqual(fake_record.drink, record.drink)

    def test_upload_container(self) -> None:
        """Test that uploading container data works without errors."""
        with self._fms as server:
            server.login()

            response = server.upload_container(
                1, 'portrait', ('sample.csv', 'col1,col2,col3,col4\nwhat,is,going,on\n')
            )

            self.assertTrue(response)
