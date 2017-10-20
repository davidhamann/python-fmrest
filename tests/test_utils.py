import unittest
from fmrest.utils import *

class UtilsTestCase(unittest.TestCase):
    """Utils test suite"""
    def setUp(self):
        pass

    def test_portal_param_string(self):
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

        params = build_portal_param_string(portals)
        self.assertEqual(
            {'portal': '["Portal1", "Portal2"]',
             'offset.Portal1': 1,
             'range.Portal1': 50,
             'offset.Portal2': 2,
             'range.Portal2': 51},
            params)
