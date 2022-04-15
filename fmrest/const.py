"""fmrest constants"""
import os
from enum import Enum, unique
from pkg_resources import get_distribution
from typing import Dict, Any

__version__ = get_distribution('python-fmrest').version

PORTAL_PREFIX = 'portal_'
TIMEOUT = int(os.environ.get('fmrest_timeout', 10))

API_VERSIONS = ('v1', 'v2', 'vLatest')
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
