"""Server class for API connections"""
import json
from .utils import request, build_portal_params
from .const import API_PATH
from .exceptions import BadJSON, FileMakerError
from .record import Record
from .foundset import Foundset

class Server(object):
    """The server class provides easy access to the FileMaker Data API

    Get an instance of this class, login, get a record, logout:

        import fmrest
        fms = fmrest.Server('https://server-address.com',
                    user='db user name',
                    password='db password',
                    database='db name',
                    layout='db layout'
                   )
        fms.login()
        fms.get_record(1)
        fms.logout()

    Or use as with statement, logging out automatically:

        with fms as my_server:
            my_server.login()
            # do stuff
    """

    def __init__(self, url, user,
                 password, database,
                 layout, verify_ssl=True):
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
            Target layout to access after login
        verify_ssl : bool, optional
            Switch to set if certificate should be verified.
            Use False to disable verification. Default True.
        """

        self.url = url
        self.user = user
        self.password = password
        self.database = database
        self.layout = layout
        self.verify_ssl = verify_ssl

        self._token = None
        self._last_fm_error = None
        self._headers = {'Content-Type': 'application/json'}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_traceback):
        self.logout()

    def __repr__(self):
        return '<Server logged_in={} database={} layout={}>'.format(
            bool(self._token), self.database, self.layout
        )

    def login(self):
        """Logs into FMServer and returns access token."""

        path = API_PATH['auth'].format(database=self.database)
        data = {
            'user': self.user,
            'password': self.password,
            'database': self.database,
            'layout': self.layout
        }

        response = self._call_filemaker('POST', path, data)

        data = response.json()
        self._token = data.get('token', None)
        self.layout = data.get('layout', None) # in case fms returns a diff layout than passed

        return self._token

    def logout(self):
        """Logs out of current session. Returns True if successful.

        Note: this method is also called by __exit__
        """

        path = API_PATH['auth'].format(database=self.database)
        self._call_filemaker('DELETE', path)

        return self.last_error == 0

    def create_record(self, field_data):
        """Creates a new record with given field data and returns new internal record id.

        Parameters
        -----------
        field_data : dict
            Dict of field names as defined in FileMaker: E.g.: {'name': 'David', 'drink': 'Coffee'}
        """
        path = API_PATH['record'].format(
            database=self.database,
            layout=self.layout,
        )

        request_data = {'data': field_data}
        response = self._call_filemaker('POST', path, request_data)
        response_data = response.json()
        record_id = response_data.get('recordId')

        return int(record_id)

    def edit(self, record, validate_mod_id=False):
        """Shortcut to edit_record method. Takes (modified) record instance and calls edit_record"""
        mod_id = record.modification_id if validate_mod_id else None
        return self.edit_record(record.record_id, record.modifications(), mod_id)

    def edit_record(self, record_id, field_data, mod_id=None):
        """Edits the record with the given record_id and field_data. Return True on success.

        Parameters
        -----------
        record_id : int
            FileMaker's internal record id.
        field_data: dict
            Dict of field names as defined in FileMaker: E.g.: {'name': 'David', 'drink': 'Coffee'}

            To delete related records, use {'deleteRelated': 'Orders.2'}, where 2 is the record id
            of the related record.

            To create a related record, use {'Orders::DeliveryTime.0':'3:07:55'}, where 0 stands for
            the record id (i.e. new record). Use an exisiting record id to edit related values.

            Note that only one related record can be created per call.
        mod_id: int, optional
            Pass a modification id to only edit the record when mod_id matches the current mod_id of
            the server. This is only supported for records in the current table, not related
            records.
        """
        # TODO: Woud be nice to be able to pass a record instance, then edit it and write the changes back to the server.
        # This would give a much cleaner interface.

        path = API_PATH['record_action'].format(
            database=self.database,
            layout=self.layout,
            record_id=record_id
        )

        request_data = {'data': field_data}
        if mod_id:
            request_data['modId'] = mod_id

        self._call_filemaker('PUT', path, request_data)

        return self.last_error == 0

    def delete_record(self, record_id):
        """Deletes a record for the given record_id. Returns True on success.

        Parameters
        -----------
        record_id : int
            FileMaker's internal record id.
        """
        path = API_PATH['record_action'].format(
            database=self.database,
            layout=self.layout,
            record_id=record_id
        )

        self._call_filemaker('DELETE', path)

        return self.last_error == 0

    def get_record(self, record_id, portals=None):
        """Fetches record with given ID and returns Record instance

        Parameters
        -----------
        record_id : int
            The FileMaker record id. Be aware that record ids CAN change (e.g. in cloned databases)
        portals : list
            A list of dicts in format [{'name':'objectName', 'offset':1, 'range':50}]

            Use this if you want to limit the amout of data returned. Offset and range are optional
            with default values of 1 and 50, respectively.
            All portals will be returned when portals==None. Default None.
        """
        path = API_PATH['record_action'].format(
            database=self.database,
            layout=self.layout,
            record_id=record_id
        )

        params = build_portal_params(portals, True) if portals else None
        response = self._call_filemaker('GET', path, params=params)

        # pass response to foundset generator function. As we are only requesting one record though,
        # we only re-use the code and immediately consume the first (and only) record via next().
        return next(self._process_foundset_response(response))

    def get_records(self, offset=1, range_=100, portals=None):
        """Requests all records in the given range, with given offset and returns result as
        Foundset instance.

        Parameters
        -----------
        offset : int, optional
            Offset for the query, starting at 1, default 1
        range_ : int, optional
            Limit the amount of returned records by providing a range. Defaults to 100
        portals : list of dicts, optional
            Define which portals you want to include in the result.
            Example: [{'name':'objectName', 'offset':1, 'range':50}]
            Defaults to None, which then returns all portals with default offset and range.
        """
        path = API_PATH['record'].format(
            database=self.database,
            layout=self.layout
        )

        params = build_portal_params(portals, True) if portals else {}
        params['offset'] = offset
        params['range'] = range_
        response = self._call_filemaker('GET', path, params=params)

        return Foundset(self._process_foundset_response(response))

    def find(self, query, sort=None, offset=1, range_=100, portals=None):
        """Finds all records matching query and returns result as a Foundset instance.

        Parameters
        -----------
        query : list of dicts
            A list of find queries, specified as 'field_name': 'field_value'
            Example:
                [{'drink': 'Coffee'}, {'drink': 'Dr. Pepper'}] will find matches for either Coffee
                or Dr. Pepper.

                You can also negate find requests by adding a key "omit" with value "true".

                Generally, all FileMaker Pro operators are supported. So, wildcard finds with "*" or
                exact matches with "==" should all work like in Pro.
        sort : list of dicts, optional
            A list of sort criteria. Example:
                [{'fieldName': 'name', 'sortOrder': 'descend'}]
        offset : int, optional
            Offset for the query, starting at 1, default 1
        range_ : int, optional
            Limit the amount of returned records by providing a range. Defaults to 100
        portals : list of dicts, optional
            Define which portals you want to include in the result.
            Example: [{'name':'objectName', 'offset':1, 'range':50}]
            Defaults to None, which then returns all portals with default offset and range.
        """
        path = API_PATH['find'].format(
            database=self.database,
            layout=self.layout
        )

        portal_params = build_portal_params(portals) if portals else None

        data = {
            'query': query,
            'sort': sort,
            'range': str(range_),
            'offset': str(offset),
            'portal': portal_params
        }

        response = self._call_filemaker('POST', path, data=data)

        return Foundset(self._process_foundset_response(response))

    def set_globals(self, globals_):
        """Set global fields for the currently active session. Returns True on success.

        Global fields do not need to be placed on the layout and can be used for establishing
        relationships of which the global is a match field.

        Parameters
        -----------
        globals_ : dict
            Dict of { field name : value }
        """
        path = API_PATH['global'].format(
            database=self.database,
            layout=self.layout
        )

        data = {'globalFields': globals_}

        self._call_filemaker('PUT', path, data=data)
        return self.last_error == 0

    @property
    def last_error(self):
        """Returns last error number returned by FileMaker Server as int.

        Error is set by _call_filemaker method. If error == -1, the previous request failed
        and no FM error code is available. If no request was made yet, last_error will be None.
        """
        if self._last_fm_error:
            error = int(self._last_fm_error)
        else:
            error = None
        return error

    def _call_filemaker(self, method, path, data=None, params=None):
        """Calls a FileMaker Server Data API path

        Parameters
        -----------
        method : str
            The http request method, e.g. POST
        path : str
            The API path, /fmi/rest/api/auth/my_solution
        data : dict of str : str, optional
            Dict of parameter data for http request
            Can be None if API expects no data, e.g. for logout
        params : dict of str : str, optional
            Dict of get parameters for http request
            Can be None if API expects no params
        """

        url = self.url + path
        data = json.dumps(data) if data else None

        # if we have a token, make sure it's included in the header
        self._update_token_header()

        response = request(method=method,
                           headers=self._headers,
                           url=url,
                           data=data,
                           verify=self.verify_ssl,
                           params=params
                          )

        try:
            response_data = response.json()
        except json.decoder.JSONDecodeError as ex:
            raise BadJSON(ex, response) from None

        self._last_fm_error = response_data.get('errorCode', -1)
        if self.last_error != 0:
            raise FileMakerError(self._last_fm_error,
                                 response_data.get('errorMessage', 'Unkown error'))

        return response

    def _update_token_header(self):
        """Update header to include access token (if available) for subsequent calls."""
        if self._token:
            self._headers['FM-Data-token'] = self._token
        return self._headers

    def _process_foundset_response(self, response):
        """Generator function that takes a response object, brings it into a Foundset/Record
        structure and yields processed Records.

        Lazily processing and yielding the results is slightly faster than building a list upfront
        when you deal with big foundsets containing records that each have many portal records.
        It won't save us much memory as we still hold the response, but initial processing time goes
        down, and we only need to build the records when we actually use them.
        (may think of another approach if it proves to be more pain than gain though)

        Parameters
        -----------
        response : requests module response
            HTTP response from the requests module
        """
        content = response.json()
        data = content['data']

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

            for portal, rows in record['portalData'].items():
                keys.append('portal_' + portal)

                # further delay creation of portal record instances
                related_records = (
                    Record(list(row), list(row.values()), in_portal=True) for row in rows
                )
                # add portal foundset to record
                values.append(Foundset(related_records))

            yield Record(keys, values)
