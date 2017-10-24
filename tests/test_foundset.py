import unittest
from fmrest.foundset import Foundset
from fmrest.record import Record

class FoundsetTestCase(unittest.TestCase):
    """Foundset test suite"""
    def setUp(self):
        pass

    def test_generator_access(self):
        """Test that passed in generator is accessible"""
        sample_gen = (i for i in [Record(['name', 'recordId'], ['john doe', 1])])
        foundset = Foundset(sample_gen)

        self.assertIsInstance(next(foundset), Record)
        with self.assertRaises(StopIteration):
            next(foundset)
