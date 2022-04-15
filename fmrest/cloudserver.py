"""Subclass of Server, specifically for connecting via the 'new' FileMaker Cloud"""
from typing import Dict, List, Optional, Union

try:
    import pycognito
except ImportError:
    _has_pycognito = False
else:
    _has_pycognito = True

from .const import API_PATH
from .server import Server

class CloudServer(Server):
    """The CloudServer class provides access to a FileMaker Cloud database. This requires authenticating with a
     Claris ID via Amazon Cognito, as described in the FileMaker 19 Data API Guide:

     https://help.claris.com/en/data-api-guide/

     Usage is otherwise identical to that of the standard fmrest Server class.

     Please note that the values for cognito_userpool_id and cognito_client_id are the same for all FileMaker Cloud
     connections at the time of writing, and thus have been provided as default values. These may, however, change in
     the future, in which case new values may be obtained per instructions here:

     https://help.claris.com/en/customer-console-help/content/create-fmid-token.html
     """

    def __init__(self,
                 url: str,
                 user: str,
                 password: str,
                 database: str,
                 layout: str,
                 cognito_userpool_id: str = 'us-west-2_NqkuZcXQY',
                 cognito_client_id: str = '4l9rvl4mv5es1eep1qe97cautn',
                 data_sources: Optional[List[Dict]] = None,
                 verify_ssl: Union[bool, str] = True,
                 type_conversion: bool = False,
                 auto_relogin: bool = False,
                 api_version: Optional[str] = None) -> None:
        """Initialize the CloudServer class.

        Parameters
        ----------
        url : str
            Address of the FileMaker Cloud Server, e.g. https://myteamname.account.filemaker-cloud.com
            Note: Data API must use https.
        user : str
            Claris ID name to log into your database
            Note: make sure it belongs to a privilege set that has fmrest extended privileges.
        password : str
            Claris ID Password to log into your database
        database : str
            Name of database without extension, e.g. Contacts
        layout : str
            Layout to work with. Can be changed between calls by setting the layout attribute again,
            e.g.: fmrest_instance.layout = 'new_layout'.
        cognito_userpool_id: str
            Amazon Cognito Userpool ID (required for FileMaker Cloud authentication).
            See https://help.claris.com/en/customer-console-help/content/create-fmid-token.html
            At time of writing, this value should be 'us-west-2_NqkuZcXQY'
        cognito_client_id:
            Amazon Cognito Client ID (required for FileMaker Cloud authentication).
            See https://help.claris.com/en/customer-console-help/content/create-fmid-token.html
            At time of writing, this value should be '4l9rvl4mv5es1eep1qe97cautn'
        data_sources : list, optional
            List of dicts in format
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

        if not _has_pycognito:
            raise ImportError(
                'Please install pycognito for Claris Cloud support. '
                'You can do so with: pip install python-fmrest[cloud]'
            )

        super().__init__(url,
                         user,
                         password,
                         database,
                         layout,
                         data_sources=data_sources,
                         verify_ssl=verify_ssl,
                         type_conversion=type_conversion,
                         auto_relogin=auto_relogin,
                         api_version=api_version)

        self.cognito_userpool_id = cognito_userpool_id
        self.cognito_client_id = cognito_client_id
        self._fmid_token = None

    def _get_cognito_token(self) -> str:
        """Use Pycognito library to authenticate with Amazon Cognito and retrieve FMID token."""

        user = pycognito.Cognito(user_pool_id=self.cognito_userpool_id,
                                 client_id=self.cognito_client_id,
                                 username=self.user)
        user.authenticate(self.password)
        return user.id_token

    def _get_bearer_token(self) -> Optional[str]:
        """Retrieve the bearer token needed to authenticate FileMaker Data API calls."""

        path = self._get_api_path('auth').format(token='')
        data = {'fmDataSource': self.data_sources}

        response = self._call_filemaker('POST', path, data=data)
        return response.get('token', None)

    def _update_token_header(self) -> Dict[str, str]:
        """Override token header update method to use FMID token if set."""

        if self._fmid_token:
            self._headers['Authorization'] = 'FMID ' + self._fmid_token
        elif self._token:
            self._headers['Authorization'] = 'Bearer ' + self._token
        else:
            self._headers.pop('Authorization', None)
        return self._headers

    def login(self) -> Optional[str]:
        """Override Server login so we obtain FMID token from Cognito first"""

        self._fmid_token = self._get_cognito_token()
        self._token = self._get_bearer_token()
        self._fmid_token = None  # Reset FMID token so auth headers are set appropriately for data api calls
        return self._token
