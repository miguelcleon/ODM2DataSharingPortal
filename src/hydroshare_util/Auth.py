from abc import ABCMeta, abstractmethod
import re
import requests
from oauthlib.oauth2 import InvalidGrantError, TokenExpiredError, UnauthorizedClientError
from hs_restclient import HydroShare, HydroShareAuthOAuth2, HydroShareAuthBasic
from . import _HydroShareUtilityBaseClass, NOT_IMPLEMENTED_ERROR
from django.shortcuts import redirect

OAUTH_ROPC = 'oauth-resource-owner-password-credentials'
OAUTH_AC = 'oauth-authorization-code'
BASIC_AUTH = 'basic-auth'


class HSUAuth(_HydroShareUtilityBaseClass):
    """
    Manager class for handling user authentication. Use 'HydroShareAuthFactory' to create instances of this class.
    :param auth: An instance of either HSUBasicAuth or HSUOAuth
    """
    def __init__(self, implementation):
        self.__implementation = implementation # type: HSUAuthImplementor

    def authenticate(self):
        return self.__implementation.authenticate()

    def get_user_info(self):
        return self.__implementation.get_user_info()

    def to_dict(self):
        return self.__implementation.to_dict()

    @staticmethod
    def authorize_client(client_id, redirect_uri, response_type):
        return HSUOAuth.authorize_client(client_id, redirect_uri, response_type)

    @staticmethod
    def authorize_client_callback(client_id, client_secret, redirect_uri, code):
        oauth = HSUOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)
        oauth._authorize_client_callback(code)
        return HSUAuth(oauth)


class HSUAuthImplementor(_HydroShareUtilityBaseClass):
    """Defines bridging interface for implementation classes"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_user_info(self):
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR)

    @abstractmethod
    def authenticate(self):
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR)

    @abstractmethod
    def to_dict(self):
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR)


class HSUOAuth(HSUAuthImplementor):
    """User authentication with OAuth 2.0 using the 'authorization_code' grant type"""
    _required_token_fields = ['response_type', 'access_token', 'token_type', 'expires_in', 'refresh_token', 'scope']
    _HS_BASE_URL_PROTO_WITH_PORT = '{scheme}://{hostname}:{port}/'
    _HS_BASE_URL_PROTO = '{scheme}://{hostname}/'
    _HS_API_URL_PROTO = '{base}hsapi/'
    _HS_OAUTH_URL_PROTO = '{base}o/'

    def __init__(self, client_id, client_secret, redirect_uri=None, use_https=True, hostname='www.hydroshare.org', port=None, scope=None,
                 access_token=None, refresh_token=None, expires_in=None, token_type='Bearer',
                 response_type='authorization_code', username=None, password=None, **kwargs):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.token_type = token_type
        self.response_type = response_type
        self.scope = scope
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_in = expires_in
        self.username = username
        self.password = password
        self.access_token = self.expires_in = self.refresh_token = None

        if use_https:
            self.scheme = 'https'
        else:
            self.scheme = 'http'

        if port is None:
            self.base_url = self._HS_BASE_URL_PROTO.format(scheme=self.scheme, hostname=hostname)
        else:
            self.base_url = self._HS_BASE_URL_PROTO_WITH_PORT.format(scheme=self.scheme, port=port, hostname=hostname)

        self.api_url = self._HS_API_URL_PROTO.format(base=self.base_url)
        self.oauth_url = self._HS_OAUTH_URL_PROTO.format(base=self.base_url)

        for key, value in kwargs.iteritems():
            setattr(self, key, value)

        if self.username and self.password:
            self._authorization_grant_type = OAUTH_ROPC
        else:
            self._authorization_grant_type = OAUTH_AC

    def get_token(self):
        token = {
            'response_type': self.response_type,
            'access_token': self.access_token,
            'token_type': self.token_type,
            'expires_in': self.expires_in,
            'refresh_token': self.refresh_token,
            'scope': self.scope
        }
        for key, value in token.iteritems():
            if value is None:
                missing_fields = [field for field in self._required_token_fields if
                                  getattr(self, field) is None and not re.search(r'^__[a-zA-Z0-9]+__$', field)]
                if len(missing_fields) > 0:
                    raise AttributeError("Missing required field(s) for 'token': [{fields}]".format(
                        classname=self.classname, fields=", ".join(missing_fields)))
        return token

    def get_user_info(self):
        # TODO: Implement...
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR)

    def authenticate(self):
        """Authenticates the user and returns a 'HydroShare' object"""
        if self._authorization_grant_type == OAUTH_AC:
            token = self.get_token()
            auth = HydroShareAuthOAuth2(self.client_id, self.client_secret, token=token)
        elif self._authorization_grant_type == OAUTH_ROPC:
            auth = HydroShareAuthOAuth2(self.client_id, self.client_secret, username=self.username,
                                        password=self.password)
        else:
            raise InvalidGrantError("Invalid authorization grant type.")

        try:
            return HydroShare(auth=auth)
        except TokenExpiredError:
            return self._refresh_authentication()

    def to_dict(self):
        # TODO: implement
        # yield self.get_user_info()
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR)

    @staticmethod
    def authorize_client(client_id, redirect_uri, response_type):
        if response_type is None:
            auth = HSUOAuth(client_id, '--not_used--', redirect_uri=redirect_uri)
        else:
            auth = HSUOAuth(client_id, '--not_used--', redirect_uri=redirect_uri, response_type=response_type)

        url = auth._get_authorization_code_url()
        return redirect(url)

    def _authorize_client_callback(self, code): # type: (str) -> None
        json_token = self._get_access_token(code)

        self.access_token = json_token['access_token']
        self.refresh_token = json_token['refresh_token']
        self.token_type = json_token['token_type']
        self.expires_in = json_token['expires_in']
        self.scope = json_token['scope']

    def _refresh_authentication(self):
        """Does the same thing as 'authenticate()', but attempts to refresh 'self.access_token' first"""
        params = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'refresh_token': self.refresh_token
        }

        url = self._build_oauth_url('token/', params)

        response = requests.post(url)

        if response.status_code == 200:
            responseJSON = response.json()

            self.access_token = responseJSON['access_token']
            self.refresh_token = responseJSON['refresh_token']
            self.expires_in = responseJSON['expires_in']
            self.scope = responseJSON['scope']

        else:
            # TODO: Use a better exception type
            raise Exception("failed to refresh access token")

        return self.authenticate()

    def _build_oauth_url(self, path, params=None): # type: (str, list) -> str
        if params is None:
            params = {}

        url_params = []
        for key, value in params.iteritems():
            url_params.append('{0}={1}'.format(key, value))

        return "{oauth_url}{path}?{params}".format(oauth_url=self.oauth_url, path=path, params="&".join(url_params))

    def _get_authorization_code_url(self):
        params = {
            'response_type': self.response_type,
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri
        }

        return self._build_oauth_url('authorize/', params)

    def _get_access_token_url(self, code):
        params = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'code': code
        }

        return self._build_oauth_url('token/', params)

    def _get_authorization_header(self):
        return {'Authorization': 'Bearer {access_token}'.format(access_token=self.access_token)}

    def _get_access_token(self, code):
        url = self._get_access_token_url(code)

        response = requests.post(url)

        if response.status_code == 200 and 'json' in dir(response):
            return response.json()
        else:
            # TODO: Better exception handling...
            raise Exception("failed to get access token")


class HSUBasicAuth(HSUAuthImplementor):
    """User authentication using 'Basic Auth' scheme."""

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_user_info(self):
        # TODO: Implement...
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR)

    def authenticate(self):
        auth = HydroShareAuthBasic(username=self.username, password=self.password)
        return HydroShare(auth=auth)

    def to_dict(self):
        # TODO: Implement...
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR)

class HSUAuthFactory(object):
    """
    This class provides a factory method for creating instances of 'HydroShareAuthManager'.

    'HydroShareAuthManager' has a required 'auth' paramater, which is an instance of either 'HSUBasicAuth'
    or 'HSUOAuth'.

    Example: Creating a 'HSUAuth' object using the 'basic' authentication scheme:
        hsauth = HSUAuthFactory.create(username='<your username>', password='<your password>')

    Example of creating a 'HSUAuth' object using the 'oauth' authentication scheme and client credential grant type:
        hsauth = HSUAuthFactory.create(username='<your_username>', password='<your_password>',
                                        client_id='<client_id>', client_secret='<client_secret>')

    Example of creating an 'HSUAuth' object using the 'auth' authentication scheme and authorization code grant type:
        token = get_token() # get_token is a stand for getting a token dictionary
        hsauth = HSUAuthFactory.create(client_id='<client_id>', client_secret='<client_secret>',
                                        token=token, redirect_uri='<your_app_redirect_uri>')
    """
    def __init__(self):
        raise NotImplementedError("'__init__' is not implemented. Use 'HydroShareAuthFactory.create(...)' to create \
        an instance of 'HydroShareAuthManager' instead.")

    @staticmethod
    def create(username=None, password=None, client_id=None, client_secret=None, token=None, redirect_uri=None):
        """
        Factory method creates and returns an instance of HSUAuth. Background implementation is determined by the
        provided paramters. The following table shows which parameters are required for each type of authentication
        scheme.

        +-----------------------------------------------------------------------------------------------------+
        |       scheme type      | username | password |   token   | client_id | client_secret | redirect_uri |
        +------------------------+----------------------------------------------------------------------------+
        | Basic Auth             |    X     |    X     |           |           |               |              |
        +------------------------+----------------------------------------------------------------------------+
        | OAuth with credentials |    X     |    X     |           |     X     |       X       |              |
        +------------------------+----------------------------------------------------------------------------+
        | OAuth with token       |          |          |     X     |     X     |       X       |      X       |
        +------------------------+----------------------------------------------------------------------------+

        :param username: user's username
        :param password: user's password
        :param client_id: application's client ID
        :param client_secret: applications client secret
        :param token: a dictionary containing values for 'access_token', 'token_type', 'refresh_token', 'expires_in',
        and 'scope'
        :param redirect_uri: redirect URI for OAuth
        """
        scheme = None
        if token and client_id and client_secret and redirect_uri:
            scheme = OAUTH_AC
        elif username and password and client_id and client_secret:
            scheme = OAUTH_ROPC
        elif username and password:
            scheme = BASIC_AUTH

        if scheme == OAUTH_AC:
            implementation = HSUOAuth(client_id, client_secret, redirect_uri, **token)
        elif scheme == OAUTH_ROPC:
            implementation = HSUOAuth(client_id, client_secret, username=username, password=password)
        elif scheme == BASIC_AUTH:
            implementation = HSUBasicAuth(username, password)
        else:
            raise ValueError("Could not determine authentication scheme with provided parameters.")

        return HSUAuth(implementation)


__all__ = ["HSUAuth", "HSUOAuth", "HSUBasicAuth", "HSUAuthFactory"]
