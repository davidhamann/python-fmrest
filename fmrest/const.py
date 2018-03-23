"""fmrest constants"""
import os
from pkg_resources import get_distribution

__version__ = get_distribution('python-fmrest').version

PORTAL_PREFIX = 'portal_'
TIMEOUT = int(os.environ.get('fmrest_timeout', 10))

API_PATH = {
    'auth':             '/fmi/data/v1/databases/{database}/sessions/{token}',
    'record':           '/fmi/data/v1/api/record/{database}/{layout}',
    'record_action':    '/fmi/data/v1/api/record/{database}/{layout}/{record_id}',
    'find':             '/fmi/data/v1/api/find/{database}/{layout}',
    'global':           '/fmi/data/v1/api/global/{database}/{layout}'
}
