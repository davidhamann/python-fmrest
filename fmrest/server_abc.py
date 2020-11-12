"""Server class for API connections"""
import abc
import json
import importlib.util
import warnings

from typing import List, Dict, Optional, Any, IO, Tuple, Union, Iterator
import requests
from .utils import build_portal_params, build_script_params, filename_from_url
from .const import API_PATH, PORTAL_PREFIX, FMSErrorCode
from .exceptions import FileMakerError
from .record import Record
from .foundset import Foundset


class ServerABC(abc.ABC):
    """The base server class provides easy access to the FileMaker Data API"""

    def __init__(self, url: str, user: str,
                 password: str, database: str, layout: str,
                 data_sources: Optional[List[Dict]] = None,
                 verify_ssl: Union[bool, str] = True,
                 type_conversion: bool = False) -> None:
        """Initialize the Server class.

        Parameters
        ----------
        url : str
            Address of the FileMaker Server, e.g. https://my-server.com or https://127.0.0.1
            Note: Data API must use https.
        user : str
            Username to log into your database
            Note: make sure it belongs to a privilege set that has fmrest extended privileges.
        password : str
            Password to log into your database
        database : str
            Name of database without extension, e.g. Contacts
        layout : str
            Layout to work with. Can be changed between calls by setting the layout attribute again,
            e.g.: fmrest_instance.layout = 'new_layout'.
        data_sources : list, optional
            List of dicts in formatj
                [{'database': 'db_file', 'username': 'admin', 'password': 'admin'}]
            Use this if for your actions you need to be authenticated to multiple DB files.
        verify_ssl : bool or str, optional
            Switch to set if certificate should be verified.
            Use False to disable verification. Default True.
            Use string path to a root cert pem file, if you work with a custom CA.
        type_conversion : bool, optional
            If True, attempt to convert string values into their potential original types.
            In previous versions of the FileMaker Data API only strings were returned and there was
            no way of knowing the correct type of a requested field value.

            Be cautious with this parameter, as results may be different from what you expect!

            Values will be converted into int, float, datetime, timedelta, string. This happens
            on a record level, not on a foundset level.
        auto_relogin : bool, optional
            If True, tries to automatically get a new token (re-login) when a
            request comes back with a 952 (invalid token) error. Defaults to
            False.
        """

        self.url = url
        self.user = user
        self.password = password
        self.database = database
        self.layout = layout
        self.data_sources = [] if data_sources is None else data_sources
        self.verify_ssl = verify_ssl

        self.type_conversion = type_conversion
        if type_conversion and not importlib.util.find_spec("dateutil"):
            warnings.warn('Turning on type_conversion needs the dateutil module, which '
                          'does not seem to be present on your system.')

        if url[:5] != 'https':
            raise ValueError('Please make sure to use https, otherwise calls to the Data '
                             'API will not work.')

        self._token: Optional[str] = None
        self._last_fm_error: Optional[int] = None
        self._last_script_result: Optional[Dict[str, List]] = None
        self._headers: Dict[str, str] = {}
        self._set_content_type()

    def login_prepare_payload(self):
        path = API_PATH['auth'].format(database=self.database, token='')
        data = {'fmDataSource': self.data_sources}
        auth = self.user, self.password
        return {
            'method': 'POST',
            'path': path,
            'data': data,
            'auth': auth,
        }

    def login_prepare_result(self, response) -> str:
        self._token = response.get('token', None)
        return self._token

    @abc.abstractmethod
    def login(self) -> Optional[str]:
        raise NotImplementedError

    def logout_prepare_payload(self) -> Dict:
        # token is expected in endpoint for logout
        path = API_PATH['auth'].format(database=self.database, token=self._token)
        self._token = ''
        return {
            'method': 'DELETE',
            'path': path,
        }

    def logout_prepare_result(self) -> bool:
        return self.last_error == FMSErrorCode.SUCCESS.value

    @abc.abstractmethod
    def logout(self) -> Optional[str]:
        raise NotImplementedError

    def create_record_prepare_payload(self, field_data: Dict[str, Any],
                                      portals: Optional[Dict[str, Any]] = None,
                                      scripts: Optional[Dict[str, List]] = None) -> Dict:
        path = API_PATH['record'].format(
            database=self.database,
            layout=self.layout,
        )

        request_data: Dict = {'fieldData': field_data}
        if portals:
            request_data['portalData'] = portals

        # build script param object in FMSDAPI style
        script_params = build_script_params(scripts) if scripts else None
        if script_params:
            request_data.update(script_params)

        return {
            'method': 'POST',
            'path': path,
            'data': request_data,
        }

    def create_record_prepare_result(self, response) -> Optional[int]:
        record_id = response.get('recordId')
        return int(record_id) if record_id else None

    @abc.abstractmethod
    def create_record(self, field_data: Dict[str, Any],
                      portals: Optional[Dict[str, Any]] = None,
                      scripts: Optional[Dict[str, List]] = None) -> Optional[int]:
        raise NotImplementedError

    def edit_record_prepare_payload(self, record_id: int, field_data: Dict[str, Any],
                                    mod_id: Optional[int] = None,
                                    portals: Optional[Dict[str, Any]] = None,
                                    scripts: Optional[Dict[str, List]] = None) -> Dict:
        path = API_PATH['record_action'].format(
            database=self.database,
            layout=self.layout,
            record_id=record_id
        )

        request_data: Dict = {'fieldData': field_data}
        if mod_id:
            request_data['modId'] = mod_id

        if portals:
            request_data['portalData'] = portals

        # build script param object in FMSDAPI style
        script_params = build_script_params(scripts) if scripts else None
        if script_params:
            request_data.update(script_params)

        return {
            'method': 'PATCH',
            'path': path,
            'data': request_data,
        }

    def edit_record_prepare_result(self) -> bool:
        return self.last_error == FMSErrorCode.SUCCESS.value

    @abc.abstractmethod
    def edit_record(self,
                    record_id: int,
                    field_data: Dict[str, Any],
                    mod_id: Optional[int] = None,
                    portals: Optional[Dict[str, Any]] = None,
                    scripts: Optional[Dict[str, List]] = None) -> bool:
        raise NotImplementedError

    def delete_record_prepare_payload(self,
                                      record_id: int,
                                      scripts: Optional[Dict[str, List]] = None):
        path = API_PATH['record_action'].format(
            database=self.database,
            layout=self.layout,
            record_id=record_id
        )

        params = build_script_params(scripts) if scripts else None
        return {
            'method': 'DELETE',
            'path': path,
            'params': params,
        }

    def delete_record_prepare_response(self):
        return self.last_error == FMSErrorCode.SUCCESS.value

    @abc.abstractmethod
    def delete_record(self, record_id: int, scripts: Optional[Dict[str, List]] = None):
        raise NotImplementedError

    def get_record_prepare_payload(self, record_id: int,
                                   portals: Optional[List[Dict]] = None,
                                   scripts: Optional[Dict[str, List]] = None,
                                   layout: Optional[str] = None):
        path = API_PATH['record_action'].format(
            database=self.database,
            layout=self.layout,
            record_id=record_id
        )

        params = build_portal_params(portals, True) if portals else {}
        params['layout.response'] = layout

        # build script param object in FMSDAPI style
        script_params = build_script_params(scripts) if scripts else None
        if script_params:
            params.update(script_params)

        return {
            'method': 'GET',
            'path': path,
            'params': params,
        }

    def get_record_prepare_result(self, response: Dict):
        return next(self._process_foundset_response(response))

    @abc.abstractmethod
    def get_record(self,
                   record_id: int,
                   portals: Optional[List[Dict]] = None,
                   scripts: Optional[Dict[str, List]] = None,
                   layout: Optional[str] = None) -> Record:
        raise NotImplementedError

    def perform_script_prepare_payload(self,
                                       name: str,
                                       param: Optional[str] = None) -> Dict:
        path = API_PATH['script'].format(
            database=self.database,
            layout=self.layout,
            script_name=name
        )
        return {
            'method': 'GET',
            'path': path,
            'params': {'script.param': param}
        }

    def perform_script_prepare_result(self, response: Dict) -> Tuple[Optional[int], Optional[str]]:
        script_error = response.get('scriptError', None)
        script_error = int(script_error) if script_error else None
        script_result = response.get('scriptResult', None)
        return script_error, script_result

    @abc.abstractmethod
    def perform_script(self,
                       name: str,
                       param: Optional[str] = None) -> Tuple[Optional[int], Optional[str]]:
        raise NotImplementedError

    def upload_container_prepare_payload(self, record_id: int,
                                         field_name: str, file_: IO) -> Dict:
        path = API_PATH['record_action'].format(
            database=self.database,
            layout=self.layout,
            record_id=record_id
        ) + '/containers/' + field_name + '/1'

        # requests library handles content type for multipart/form-data incl. boundary
        self._set_content_type(False)
        return {
            'method': 'POST',
            'path': path,
            'files': {'upload': file_},
        }

    def upload_container_prepare_result(self) -> bool:
        return self.last_error == FMSErrorCode.SUCCESS.value

    def upload_container(self, record_id: int, field_name: str, file_: IO) -> bool:
        raise NotImplementedError

    def get_records_prepare_payload(self, offset: int = 1, limit: int = 100,
                                    sort: Optional[List[Dict[str, str]]] = None,
                                    portals: Optional[List[Dict[str, Any]]] = None,
                                    scripts: Optional[Dict[str, List]] = None,
                                    layout: Optional[str] = None):
        path = API_PATH['record'].format(
            database=self.database,
            layout=self.layout
        )

        params = build_portal_params(portals, True) if portals else {}
        params['_offset'] = offset
        params['_limit'] = limit
        params['layout.response'] = layout

        if sort:
            params['_sort'] = json.dumps(sort)

        # build script param object in FMSDAPI style
        script_params = build_script_params(scripts) if scripts else None
        if script_params:
            params.update(script_params)

        return {
            'method': 'GET',
            'path': path,
            'params': params,
        }

    def get_records_prepare_result(self, response: Dict) -> Foundset:
        info = response.get('dataInfo', {})
        return Foundset(self._process_foundset_response(response), info)

    def get_records(self,
                    offset: int = 1,
                    limit: int = 100,
                    sort: Optional[List[Dict[str, str]]] = None,
                    portals: Optional[List[Dict[str, Any]]] = None,
                    scripts: Optional[Dict[str, List]] = None,
                    layout: Optional[str] = None) -> Foundset:
        raise NotImplementedError

    def find_prepare_payload(self, query: List[Dict[str, Any]],
                             sort: Optional[List[Dict[str, str]]] = None,
                             offset: int = 1, limit: int = 100,
                             portals: Optional[List[Dict[str, Any]]] = None,
                             scripts: Optional[Dict[str, List]] = None,
                             layout: Optional[str] = None) -> Dict:
        path = API_PATH['find'].format(
            database=self.database,
            layout=self.layout
        )

        data = {
            'query': query,
            'sort': sort,
            'limit': str(limit),
            'offset': str(offset),
            'layout.response': layout
        }

        # build script param object in FMSDAPI style
        script_params = build_script_params(scripts) if scripts else None
        if script_params:
            data.update(script_params)

        # build portal param object in FMSDAPI style
        portal_params = build_portal_params(portals) if portals else None
        if portal_params:
            data.update(portal_params)

        # FM Data API from v17 cannot handle null values, so we remove all Nones from data
        data = {k: v for k, v in data.items() if v is not None}
        return {
            'method': 'POST',
            'path': path,
            'data': data,
        }

    def find_prepare_result(self, response: Dict) -> Foundset:
        info = response.get('dataInfo', {})
        return Foundset(self._process_foundset_response(response), info)

    def find(self, query: List[Dict[str, Any]],
             sort: Optional[List[Dict[str, str]]] = None,
             offset: int = 1, limit: int = 100,
             portals: Optional[List[Dict[str, Any]]] = None,
             scripts: Optional[Dict[str, List]] = None,
             layout: Optional[str] = None) -> Foundset:
        raise NotImplementedError

    def fetch_file_prepare_payload(self, file_url: str,
                                   stream: bool = False) -> Dict:
        return {
            'method': 'get',
            'url': file_url,
            'verify': self.verify_ssl,
            'stream': stream,
        }

    def fetch_file_prepare_result(self, file_url: str, response: Any):
        name = filename_from_url(file_url)
        return (name,
                response.headers.get('Content-Type'),
                response.headers.get('Content-Length'),
                response)


    def fetch_file(self,
                   file_url: str,
                   stream: bool = False) -> Tuple[str, Optional[str], Optional[str], requests.Response]:
        raise NotImplementedError

    def set_globals_prepare_payload(self, globals_: Dict[str, Any]) -> Dict:
        path = API_PATH['global'].format(database=self.database)
        data = {'globalFields': globals_}
        return {
            'method': 'PATCH',
            'path': path,
            'data': data,
        }

    def set_globals_prepare_result(self):
        return self.last_error == FMSErrorCode.SUCCESS.value

    def set_globals(self, globals_: Dict[str, Any]) -> bool:
        raise NotImplementedError

    @property
    def last_error(self) -> Optional[int]:
        """Returns last error number returned by FileMaker Server as int.

        Error is set by _call_filemaker method. If error == -1, the previous request failed
        and no FM error code is available. If no request was made yet, last_error will be None.
        """
        error: Optional[int]

        if self._last_fm_error:
            error = int(self._last_fm_error)
        else:
            error = None
        return error

    @property
    def last_script_result(self) -> Dict:
        """Returns last script results as returned by FMS as dict in format {type: [error, result]}

        Only returns keys that have a value from the last call. I.e. 'presort' will
        only be present if the last call performed a presort script.
        The returned error (0th element in list) will always be converted to int.
        """
        result: Dict = {}

        if self._last_script_result:
            result = {
                k: [int(v[0]), v[1]] for k, v in self._last_script_result.items() if v[0] is not None
            }
        return result

    def _update_script_result(self, response: Dict) -> Dict[str, List]:
        """Extracts script result data from fms response and updates script result attribute"""
        self._last_script_result = {
            'prerequest': [
                response.get('scriptError.prerequest', None),
                response.get('scriptResult.prerequest', None)
            ],
            'presort': [
                response.get('scriptError.presort', None),
                response.get('scriptResult.presort', None)
            ],
            'after': [
                response.get('scriptError', None),
                response.get('scriptResult', None)
            ]
        }

        return self._last_script_result

    def _update_token_header(self) -> Dict[str, str]:
        """Update header to include access token (if available) for subsequent calls."""
        if self._token:
            self._headers['Authorization'] = 'Bearer ' + self._token
        else:
            self._headers.pop('Authorization', None)
        return self._headers

    def _set_content_type(self, type_: Union[str, bool] = 'application/json') -> Dict[str, str]:
        """Set the Content-Type header and returns the updated _headers dict.

        Parameters
        -----------
        type_ : str, boolean
            String definining the content type for the HTTP header or False to remove the
            Content-Type key from _headers (i.e. let the requests lib handle the Content-Type.)
        path : str
        """
        if isinstance(type_, str):
            self._headers['Content-Type'] = type_
        elif not type_:
            self._headers.pop('Content-Type')
        else:
            raise ValueError
        return self._headers

    def _process_foundset_response(self, response: Dict) -> Iterator[Record]:
        """Generator function that takes a response object, brings it into a Foundset/Record
        structure and yields processed Records.

        Lazily processing and yielding the results is slightly faster than building a list upfront
        when you deal with big foundsets containing records that each have many portal records.
        It won't save us much memory as we still hold the response, but initial processing time goes
        down, and we only need to build the records when we actually use them.
        (may think of another approach if it proves to be more pain than gain though)

        Parameters
        -----------
        response : dict
            FMS response from a _call_filemaker request
        """
        data = response['data']

        for record in data:
            field_data = record['fieldData']

            # Add meta fields to record.
            # TODO: this can clash with fields that have the same name. Find a better
            # way (maybe prefix?).
            # Note that portal foundsets have the recordId field included by default
            # (without the related table prefix).
            field_data['recordId'] = record.get('recordId')
            field_data['modId'] = record.get('modId')

            keys = list(field_data)
            values = list(field_data.values())

            portal_info = {}
            for entry in record.get('portalDataInfo', []):
                # a portal is identified by its object name, or, if not available, its TO name
                portal_identifier = entry.get('portalObjectName', entry['table'])
                portal_info[portal_identifier] = entry

            for portal_name, rows in record['portalData'].items():
                keys.append(PORTAL_PREFIX + portal_name)

                # further delay creation of portal record instances
                related_records = (
                    Record(list(row), list(row.values()),
                           in_portal=True, type_conversion=self.type_conversion
                           ) for row in rows
                )
                # add portal foundset to record
                values.append(Foundset(related_records, portal_info.get(portal_name, {})))

            yield Record(keys, values, type_conversion=self.type_conversion)

    def handle_response_data(self, response_data: Dict) -> Dict:
        fms_messages = response_data.get('messages')
        fms_response = response_data.get('response')

        self._update_script_result(fms_response)
        self._last_fm_error = fms_messages[0].get('code', -1)
        if self.last_error != FMSErrorCode.SUCCESS.value:
            raise FileMakerError(self._last_fm_error,
                                 fms_messages[0].get('message', 'Unkown error'))

        self._set_content_type()  # reset content type

        return fms_response
