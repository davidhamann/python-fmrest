"""Utility functions for fmrest"""
import requests
from .exceptions import RequestException
from .const import TIMEOUT

"""
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
        raise RequestException(ex, args, kwargs)
