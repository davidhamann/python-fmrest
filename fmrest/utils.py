"""Utility functions for fmrest"""
import requests
from .exceptions import RequestException
from .const import TIMEOUT

"""
# http://docs.python-requests.org/en/master/api/#api-changes
#--- DEBUG
import logging
import http.client as http_client

http_client.HTTPConnection.debuglevel = 1

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

#--- DEBUG
"""


def request(*args, **kwargs):
    """Wrapper around requests library request call"""
    try:
        return requests.request(*args, timeout=TIMEOUT, **kwargs)
    except Exception as ex:
        raise RequestException(ex, args, kwargs) from None

def build_portal_param_string(portals):
    """Takes a list of dicts and returns a dict in a format as FMServer expects it

    FMS expects portals and their options to be specified in the following format:
        portal=["Portal1", "Portal2"]&offset.Portal1=1&range.Portal1=10

    This function will return a dict of params suitable for the requests module.

    Parameters
    -----------
    portals : list
        List of dicts with keys name, offset, range
        Example:
            [
                {
                    'name': 'addressPortal', # FM object name of portal
                    'offset': 1,
                    'range': 50
                },
                {
                    'name': 'notesPortal',
                    'offset': 1,
                    'range': 50
                }
            ]
    """

    portal_selector = [portal['name'] for portal in portals]
    portal_param = "[" + ', '.join(map(lambda x: '"' + x + '"', portal_selector)) + "]"
    params = {"portal": portal_param}

    for portal in portals:
        params['offset.' + portal['name']] = portal.get('offset', 1)
        params['range.' + portal['name']] = portal.get('range', 50)

    return params
