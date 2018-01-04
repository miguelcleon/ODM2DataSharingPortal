import os
from abc import ABCMeta, abstractmethod
import re
import requests
from oauthlib.oauth2 import InvalidGrantError, TokenExpiredError
from hs_restclient import HydroShare, HydroShareAuthOAuth2, HydroShareAuthBasic
from . import HydroShareUtilityBaseClass, NOT_IMPLEMENTED_ERROR


OAUTH_CLIENT_CREDENTIALS = 'oauth-client-credentials'
OAUTH_AUTHORIZATION_CODE = 'oauth-authorization-code'
BASIC_AUTH = 'basic-auth'


class HSUAuth(HydroShareUtilityBaseClass):
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


class HSUAuthImplementor(HydroShareUtilityBaseClass):
    """Defines bridging interface for implementation classes"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_user_info(self):
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR)

    @abstractmethod
    def authenticate(self):
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR)


class HSUOAuth(HSUAuthImplementor):
    """User authentication with OAuth 2.0 using the 'authorization_code' grant type"""
    _required_token_fields = ['response_type', 'access_token', 'token_type', 'expires_in', 'refresh_token', 'scope']
    _HS_BASE_URL_PROTO_WITH_PORT = '{scheme}://{hostname}:{port}/'
    _HS_BASE_URL_PROTO = '{scheme}://{hostname}/'
    _HS_API_URL_PROTO = '{base}hsapi/'
    _HS_TOKEN_URL_PROTO = '{base}o/'

    def __init__(self, client_id, client_secret, use_https=True, hostname='www.hydroshare.org', port=None, scope=None,
                 access_token=None, refresh_token=None, expires_in=None, token_type='Bearer',
                 response_type='authorization_code', username=None, password=None, **kwargs):
        self.client_id = client_id
        self.client_secret = client_secret
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
        self.token_url = self._HS_TOKEN_URL_PROTO.format(base=self.base_url)

        for key, value in kwargs.iteritems():
            setattr(self, key, value)

        if self.username and self.password:
            self._authorization_grant_type = OAUTH_CLIENT_CREDENTIALS
        else:
            self._authorization_grant_type = OAUTH_AUTHORIZATION_CODE

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
        if self._authorization_grant_type == OAUTH_AUTHORIZATION_CODE:
            token = self.get_token()
            auth = HydroShareAuthOAuth2(self.client_id, self.client_secret, token=token)
        elif self._authorization_grant_type == OAUTH_CLIENT_CREDENTIALS:
            auth = HydroShareAuthOAuth2(self.client_id, self.client_secret, username=self.username,
                                        password=self.password)
        else:
            raise InvalidGrantError("Invalid authorization grant type.")

        try:
            return HydroShare(auth=auth)
        except TokenExpiredError:
            return self._refresh_authentication()

    def _refresh_authentication(self):
        """Gets a new access token"""
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR)


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


class HSUAuthFactory(object):
    """
    This class provides a factory method for creating instances of 'HydroShareAuthManager'.

    'HydroShareAuthManager' has a required 'auth' paramater, which is an instance of either 'HSUBasicAuth'
    or 'HSUOAuth'.

    Example: Creating a 'HSUAuth' object using the 'basic' authentication scheme:
        hsauth = HSUAuthFactory.factory(username='<your username>', password='<your password>')

    Example of creating a 'HSUAuth' object using the 'oauth' authentication scheme and client credential grant type:
        hsauth = HSUAuthFactory.factory(username='<your_username>', password='<your_password>',
                                        client_id='<client_id>', client_secret='<client_secret>')

    Example of creating an 'HSUAuth' object using the 'auth' authentication scheme and authorization code grant type:
        token = get_token() # get_token is a stand for getting a token dictionary
        hsauth = HSUAuthFactory.factory(client_id='<client_id>', client_secret='<client_secret>',
                                        token=token, redirect_uri='<your_app_redirect_uri>')
    """
    def __init__(self):
        raise NotImplementedError("'__init__' is not implemented. Use 'HydroShareAuthFactory.factory(...)' to create \
        an instance of 'HydroShareAuthManager' instead.")

    @staticmethod
    def factory(username=None, password=None, client_id=None, client_secret=None, token=None, redirect_uri=None):
        """
        Factory method creates and returns an instance of HSUAuth. Background implementation is determined by the
        provided paramters. The following table shows which parameters are required for each type of authentication
        scheme.

        +----------------------------------------------------------------------------------------------------+
        |   Auth Scheme Type     | username | password |  token   | client_id | client_secret | redirect_uri |
        +------------------------+---------------------------------------------------------------------------+
        | Basic Auth             |    X     |    X     |          |           |               |              |
        +------------------------+---------------------------------------------------------------------------+
        | OAuth with credentials |    X     |    X     |          |     X     |       X       |              |
        +------------------------+---------------------------------------------------------------------------+
        | OAuth with token       |          |          |    X     |     X     |       X       |      X       |
        +------------------------+---------------------------------------------------------------------------+

        :param username: user's username
        :param password: user's password
        :param client_id: application's client ID
        :param client_secret: applications client secret
        :param token: a dictionary containing values for 'access_token', 'token_type', 'refresh_token', 'expires_in',
        and 'scope'
        :param redirect_uri: redirect URI for OAuth
        """
        scheme = None
        if username and password and client_id and client_secret:
            scheme = OAUTH_CLIENT_CREDENTIALS
        elif token and client_id and client_secret and redirect_uri:
            scheme = OAUTH_AUTHORIZATION_CODE
        elif username and password:
            scheme = BASIC_AUTH

        if scheme == OAUTH_AUTHORIZATION_CODE:
            implementation = HSUOAuth(client_id, client_secret, **token)
        elif scheme == OAUTH_CLIENT_CREDENTIALS:
            implementation = HSUOAuth(client_id, client_secret, username=username, password=password)
        elif scheme == BASIC_AUTH:
            implementation = HSUBasicAuth(username, password)
        else:
            raise ValueError("Could not determine authentication scheme with provided parameters.")

        return HSUAuth(implementation)
