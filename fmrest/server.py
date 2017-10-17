"""Server class for API connections"""
import json
from .utils import request
from .const import API_PATH
from .exceptions import BadJSON, FileMakerError


class Server(object):
    """The server class provides easy access to the FileMaker Data API

    Get an instance of this class:

        import fmrest
        fms = fmrest.Server('https://server-address.com',
                    user='db user name',
                    password='db password',
                    database='db name',
                    layout='db layout'
                   )
    """

    def __init__(self, url, user,
                 password, database,
                 layout, verifySSL=True):
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
        verifySSL : bool, optional
            Switch to set if certificate should be verified.
            Use False to disable verification. Default True.
        """

        self.url = url
        self.user = user
        self.password = password
        self.database = database
        self.layout = layout
        self.verifySSL = verifySSL

        self._token = None
        self._last_fm_error = None
        self._headers = {'Content-Type': 'application/json'}

    def login(self):
        """Logs into FMServer and returns access token."""

        path = API_PATH['auth'].format(database=self.database)
        data = {
            'user': self.user,
            'password': self.password,
            'database': self.database,
            'layout': self.layout
        }

        response = self._call_filemaker('POST', self._headers, path, data)

        data = response.json()
        self._token = data.get('token', None)
        self.layout = data.get('layout', None) # in case fms returns a diff layout than passed

        return self._token

    def logout(self):
        """Logs out of current session. Returns True if successful.

        Note: this method is also called by __exit__"""

        path = API_PATH['auth'].format(database=self.database)
        headers = self._update_token_header()
        self._call_filemaker('DELETE', headers, path)

        return self.last_error == '0'

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

    def _call_filemaker(self, method, headers, path, data=None):
        """Calls a FileMaker Server Data API path

        Parameters
        -----------
        method : str
            The http request method, e.g. POST
        headers : dict of str : str
            Dict of http headers for the request
        path : str
            The API path, /fmi/rest/api/auth/my_solution
        data : dict of str : str, optional
            Dict of parameter data for http request
            Can be None if API expects no data, e.g. for logout
        """

        url = self.url + path
        data = json.dumps(data) if data else None

        response = request(method=method,
                           headers=headers,
                           url=url,
                           data=data,
                           verify=self.verifySSL
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
        """Update header to include access token for subsequent calls."""
        self._headers['FM-Data-token'] = self._token
        return self._headers

    def __enter__(self):
        return self

    def __exit__(self, exc, val, traceback):
        self.logout()

    def __repr__(self):
        return '<Server logged_in={} database={}>'.format(bool(self._token), self.database)
