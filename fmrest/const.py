"""fmrest constants"""
import os
from enum import Enum, unique
from typing import Dict, Any

PACKAGE_NAME = 'python-fmrest'

try:
    from importlib.metadata import version  # Python 3.8+
    __version__ = version(PACKAGE_NAME)
except ImportError:
    from pkg_resources import get_distribution  # Python 3.6-3.7
    __version__ = get_distribution(PACKAGE_NAME).version

PORTAL_PREFIX = 'portal_'
TIMEOUT = int(os.environ.get('fmrest_timeout', 10))

API_VERSIONS = ('v1', 'v2', 'vLatest')
API_DATE_FORMATS = [('us', '0'), ('file', '1'), ('iso-8601', '2')]
API_PATH_PREFIX = '/fmi/data/{version}'
API_PATH: Dict[str, Any] = {
    'meta': {
        'product':      '/productInfo',
        'databases':    '/databases',
        'layouts':      '/databases/{database}/layouts',
        'scripts':      '/databases/{database}/scripts'
    },
    'auth':             '/databases/{database}/sessions/{token}',
    'record':           '/databases/{database}/layouts/{layout}/records',
    'record_action':    '/databases/{database}/layouts/{layout}/records/{record_id}',
    'find':             '/databases/{database}/layouts/{layout}/_find',
    'script':           '/databases/{database}/layouts/{layout}/script/{script_name}',
    'global':           '/databases/{database}/globals'
}


@unique
class FMSErrorCode(Enum):
    """FMS error codes that are being referenced in the code"""
    SUCCESS = 0
    RECORD_MISSING = 101
    INVALID_USER_PASSWORD = 212
    INVALID_DAPI_TOKEN = 952
