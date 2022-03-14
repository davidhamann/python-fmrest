"""fmrest constants"""
import os
from enum import Enum, unique
from pkg_resources import get_distribution

__version__ = get_distribution('python-fmrest').version

PORTAL_PREFIX = 'portal_'
TIMEOUT = int(os.environ.get('fmrest_timeout', 10))

API_PATH = {
    'meta': {
        'productinfo':      '/fmi/data/v1/productInfo',
        'databasenames':    '/fmi/data/v1/databases',
        'layoutnames':      '/fmi/data/v1/databases/{database}/layouts',
        'scriptnames':      '/fmi/data/v1/databases/{database}/scripts',
        'layoutmetadata':   '/fmi/data/v1/databases/{database}/layouts/{layout}'
    },
    'auth':             '/fmi/data/v1/databases/{database}/sessions/{token}',
    'record':           '/fmi/data/v1/databases/{database}/layouts/{layout}/records',
    'record_action':    '/fmi/data/v1/databases/{database}/layouts/{layout}/records/{record_id}',
    'find':             '/fmi/data/v1/databases/{database}/layouts/{layout}/_find',
    'script':           '/fmi/data/v1/databases/{database}/layouts/{layout}/script/{script_name}',
    'global':           '/fmi/data/v1/databases/{database}/globals'
}


@unique
class FMSErrorCode(Enum):
    """FMS error codes that are being referenced in the code"""
    SUCCESS = 0
    RECORD_MISSING = 101
    INVALID_USER_PASSWORD = 212
    INVALID_DAPI_TOKEN = 952
