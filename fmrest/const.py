"""fmrest constants"""
import os
from pkg_resources import get_distribution

__version__ = get_distribution('python-fmrest').version

PORTAL_PREFIX = 'portal_'
TIMEOUT = int(os.environ.get('fmrest_timeout', 10))

API_PATH = {
    'auth':             '/fmi/rest/api/auth/{database}',
    'record':           '/fmi/rest/api/record/{database}/{layout}',
    'record_action':    '/fmi/rest/api/record/{database}/{layout}/{record_id}',
    'find':             '/fmi/rest/api/find/{database}/{layout}',
    'global':           '/fmi/rest/api/global/{database}/{layout}'
}
