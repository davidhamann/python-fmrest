import unittest
import datetime
from fmrest.utils import *

class UtilsTestCase(unittest.TestCase):
    """Utils test suite"""
    def setUp(self):
        pass

    def test_portal_params(self):
        """Test that portal param string is build correctly."""
        portals = [
            {
                'name': 'Portal1',
                'offset': 1,
                'range': 50
            },
            {
                'name': 'Portal2',
                'offset': 2,
                'range': 51
            }
        ]

        params = build_portal_params(portals, names_as_string=True)
        self.assertEqual(
            {'portal': '["Portal1", "Portal2"]',
             'offset.Portal1': 1,
             'range.Portal1': 50,
             'offset.Portal2': 2,
             'range.Portal2': 51},
            params)

        params = build_portal_params(portals)
        self.assertEqual(
            {'portal': ["Portal1", "Portal2"],
             'offset.Portal1': 1,
             'range.Portal1': 50,
             'offset.Portal2': 2,
             'range.Portal2': 51},
            params)

    def test_string_to_time_conversion(self):
        """Test that strings can be converted into their "guessed" original types."""

        self.assertEqual(
            convert_string_type('23:59:59'),
            datetime.timedelta(hours=23, minutes=59, seconds=59)
        )

        self.assertEqual(
            convert_string_type('48:61:01'),
            datetime.timedelta(days=2, hours=1, minutes=1, seconds=1)
        )

        self.assertEqual(
            convert_string_type('aa:bb:cc'),
            'aa:bb:cc' #remains string
        )

    def test_string_to_datetime_conversion(self):
        """Test that strings can be converted into their "guessed" original types."""

        self.assertEqual(
            convert_string_type('12/24/2016'),
            datetime.datetime(2016, 12, 24)
        )

        self.assertEqual(
            convert_string_type('12/01/2017 20:45:30'),
            datetime.datetime(2017, 12, 1, 20, 45, 30)
        )

        self.assertEqual(
            convert_string_type('12/01/0001 20:45:30'),
            datetime.datetime(1, 12, 1, 20, 45, 30)
        )

    def test_string_to_number_conversion(self):
        """Test that strings can be converted into their "guessed" original types."""

        self.assertIsInstance(
            convert_string_type('42'),
            int
        )

        self.assertIsInstance(
            convert_string_type('42.1'),
            float
        )

        self.assertIsInstance(
            convert_string_type('no. 42'),
            str
        )

    def test_filename_from_url(self):
        """Test that we can extract the file name from a FM RC URL."""

        # filename without extension
        filename = '7124058BDBFC7C4BB82331184A3C72BC4EB0C449FCF35DBA295B3A448FD142EB'
        self.assertEqual(
            filename_from_url(
                'https://10.211.55.15/Streaming_SSL/MainDB/'
                '7124058BDBFC7C4BB82331184A3C72BC4EB0C449FCF35DBA295B3A448FD142EB'
                '?RCType=EmbeddedRCFileProcessor'),
            filename)

        # filename with extension
        filename = '6DE110C449E23F7C196F87CC062046A7BE48927BBEB90F5B0A4BFA809A249075.mp4'
        self.assertEqual(
            filename_from_url(
                'https://10.211.55.15/Streaming_SSL/MainDB/'
                '6DE110C449E23F7C196F87CC062046A7BE48927BBEB90F5B0A4BFA809A249075.mp4'
                '?RCType=EmbeddedRCFileProcessor'),
            filename)
