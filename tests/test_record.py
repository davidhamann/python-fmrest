import unittest
from fmrest.record import Record

class RecordTestCase(unittest.TestCase):
    """Server test suite"""
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
