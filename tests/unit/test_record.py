import unittest
from fmrest.record import Record

class RecordTestCase(unittest.TestCase):
    """Record test suite"""
    def setUp(self):
        pass

    def test_key_value_mismatch_handling(self):
        """Test that Record cannot be initialized with a key-value length mismatch."""
        with self.assertRaises(ValueError):
            Record(['key1', 'key2'], [1])

        with self.assertRaises(ValueError):
            Record(['key1'], [1, 2])

    def test_key_access(self):
        """Test that Record keys and values can be accessed."""
        assert_name = 'David'
        assert_drink = 'Coffee'

        record = Record(['name', 'drink'], [assert_name, assert_drink])

        self.assertEqual(record.keys(), ['name', 'drink'])
        self.assertEqual(record.values(), [assert_name, assert_drink])
        
        self.assertEqual(record.name, assert_name)
        self.assertEqual(record['name'], assert_name)

        self.assertEqual(record.drink, assert_drink)
        self.assertEqual(record['drink'], assert_drink)

        with self.assertRaises(KeyError):
            record['city']

        with self.assertRaises(AttributeError):
            record.city

    def test_dirty_record_flagging(self):
        """Test that a record gets flagged as dirty when you change its value."""
        assert_name = 'David'
        assert_drink = 'Coffee'

        # setting the same value should not flag as dirty
        record = Record(['name', 'drink'], [assert_name, assert_drink])
        record.name = 'David'
        self.assertFalse(record.is_dirty)

        # ... again for dict access
        record = Record(['name', 'drink'], [assert_name, assert_drink])
        record['name'] = 'David'
        self.assertFalse(record.is_dirty)

        # now do change the value
        record = Record(['name', 'drink'], [assert_name, assert_drink])
        record.name = 'Caspar'
        self.assertTrue(record.is_dirty)

        record = Record(['name', 'drink'], [assert_name, assert_drink])
        record['name'] = 'Caspar'
        self.assertTrue(record.is_dirty)

    def test_key_error_on_invalid_keys(self):
        """Test that trying to set a non-existing key will raise an error."""
        record = Record(['name'], ['David'])

        with self.assertRaises(AttributeError):
            record.drink = 'Dr. Pepper'

        with self.assertRaises(KeyError):
            record['city'] = 'Hamburg'

    def test_setting_class_slots(self):
        """Test that slots can be set w/o being intercepted and written to the modification dict."""
        record = Record(['name'], ['David'])
        record._keys = ['drink']

        self.assertIn('drink', record.keys())

    def test_modification_tracking(self):
        """Test that record modifications are tracked."""
        fake_modifications = {
            'drink': 'Dr. Pepper',
            'city': 'New York'
        }

        record = Record(['name', 'drink', 'city'], ['David', 'Coffee', 'Hamburg'])
        record.name = 'David' # should not be flagged as it is the same value
        record.drink = 'Dr. Pepper'
        record.city = 'New York'

        self.assertEqual(fake_modifications, record.modifications())

    def test_setting_portal_data_error(self):
        """Test that attempting to set portal data raises an error.
        Once supported, this test can be replaced by a test, that verifies portal data can be set.
        """
        record = Record(['name', 'portal_notes'], ['David', 'dummy'])

        with self.assertRaises(KeyError):
            record['portal_notes'] = 1234

    def test_dict_conversion(self):
        """Test that a record can be converted into a dict structure."""
        record = Record(
            ['name', 'drink', 'city', 'portal_notes', 'portal_addresses'],
            ['David', 'Coffee', 'Hamburg', 'dummy', 'dummy2']
        )

        fake_dict = {
            'name': 'David',
            'drink': 'Coffee',
            'city': 'Hamburg',
            'portal_notes': 'dummy',
            'portal_addresses': 'dummy2'
        }

        self.assertEqual(record.to_dict(), fake_dict)

        # test without portals
        fake_dict.pop('portal_notes')
        fake_dict.pop('portal_addresses')
        self.assertEqual(record.to_dict(ignore_portals=True), fake_dict)
