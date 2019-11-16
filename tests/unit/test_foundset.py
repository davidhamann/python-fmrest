import unittest
from fmrest.foundset import Foundset
from fmrest.record import Record

class FoundsetTestCase(unittest.TestCase):
    """Foundset test suite"""
    def setUp(self) -> None:
        pass

    def test_index_access(self) -> None:
        """Test that values in generator are accesible via their index. Values are cached,
        so we are actually testing that we can access the cached list."""
        sample_gen = (record for record in [
            Record(['name', 'recordId'], ['john doe', 1], True),
            Record(['name', 'recordId'], ['john smith', 2], True),
            Record(['name', 'recordId'], ['john wayne', 3], True)
        ])
        foundset = Foundset(sample_gen)

        self.assertEqual(foundset[1].name, 'john smith')

        # Accessing an out of range index of cached values should raise IndexError
        with self.assertRaises(IndexError):
            foundset[3]

    def test_list_builduing(self) -> None:
        """Test that building a list works with generated and cached values"""

        sample_gen = Foundset(i for i in [1, 2, 4, 5, 6, 7, 8])
        self.assertEqual(list(zip(sample_gen, sample_gen)), list(zip(sample_gen, sample_gen)))

    def test_info(self) -> None:
        """Test that info section is available."""
        info = {'portalObjectName': 'sample', 'database': 'DB', 'table': 'Sample', 'foundCount': 69, 'returnedCount': 50}
        sample_gen = Foundset((i for i in [1, 2]), info)
        self.assertEqual(sample_gen.info, info)

    def test_empty_info(self) -> None:
        """Test that a foundset without 'dataInfo' section returns an empty info dictionary"""

        sample_gen = Foundset(i for i in [1, 2])
        self.assertEqual(sample_gen.info, {})
