from abc import ABCMeta, abstractmethod, abstractproperty
import re
import requests
import logging as logger
from oauthlib.oauth2 import InvalidGrantError, TokenExpiredError, UnauthorizedClientError
from hs_restclient import HydroShareAuthOAuth2, HydroShareAuthBasic
from utility import HydroShareAdapter
from . import HydroShareUtilityBaseClass, NOT_IMPLEMENTED_ERROR
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseServerError

DEFAULT_RESPONSE_TYPE = 'code'

OAUTH_ROPC = 'oauth-resource-owner-password-credentials'
OAUTH_AC = 'oauth-authorization-code'
BASIC_AUTH = 'basic'

class HSUAuth(HydroShareUtilityBaseClass):
    """Main authentication class. Use 'HSUAuthFactory' to create instances of this class."""
    def __init__(self, implementation):
        self.__implementation = implementation

    @property
    def auth_type(self):
        return self.__implementation.auth_type

    def get_client(self):
        return self.__implementation.get_client()

    def get_user_info(self):
        return self.__implementation.get_user_info()

    def get_token(self):
        return self.__implementation.get_token()

    @staticmethod
    def authorize_client(client_id, redirect_uri, response_type=None):
        return HSUOAuth.authorize_client(client_id, redirect_uri, response_type=response_type)

    @staticmethod
    def authorize_client_callback(client_id, client_secret, redirect_uri, code):
        oauth = HSUOAuth.authorize_client_callback(client_id, client_secret, redirect_uri, code)
        auth = HSUAuth(oauth)
        return auth


class HSUAuthImplementor(HydroShareUtilityBaseClass):
    """Defines bridging interface for implementation classes of 'HSUAuth'"""
    __metaclass__ = ABCMeta

    @abstractproperty
    def auth_type(self):
        pass

    @abstractmethod
    def get_user_info(self):
        pass

    @abstractmethod
    def get_client(self):
        pass

    @abstractmethod
    def get_token(self):
        pass


class HSUOAuth(HSUAuthImplementor):
    """User authentication with OAuth 2.0 using the 'authorization_code' grant type"""
    _required_token_fields = ['response_type', 'access_token', 'token_type', 'expires_in', 'refresh_token', 'scope']
    _HS_BASE_URL_PROTO_WITH_PORT = '{scheme}://{hostname}:{port}/'
    _HS_BASE_URL_PROTO = '{scheme}://{hostname}/'
    _HS_API_URL_PROTO = '{base}hsapi/'
    _HS_OAUTH_URL_PROTO = '{base}o/'

    def __init__(self, client_id, client_secret, redirect_uri=None, use_https=True, hostname='www.hydroshare.org',
                 port=None, scope=None, access_token=None, refresh_token=None, expires_in=None, token_type='Bearer',
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
            if key in self.__dict__:
                setattr(self, key, value)

        if self.username and self.password:
            self._authorization_grant_type = OAUTH_ROPC
        else:
            self._authorization_grant_type = OAUTH_AC

    @property
    def auth_type(self):
        return self._authorization_grant_type

    def get_token(self):
        token = {
            'access_token': self.access_token,
            'token_type': self.token_type,
            'expires_in': self.expires_in,
            'refresh_token': self.refresh_token,
            'scope': self.scope
        }
        for key, value in token.iteritems():
            if value is None:
                missing_attrs = [field for field in self._required_token_fields if
                                  getattr(self, field) is None and not re.search(r'^__[a-zA-Z0-9]+__$', field)]
                if len(missing_attrs) > 0:
                    raise AttributeError("missing attributes(s) for token: {attrs}".format(attrs=missing_attrs))
        return token

    def get_user_info(self):
        session = requests.Session()

        header = self._get_authorization_header()
        url = "{url_base}{path}".format(url_base=self.api_url, path='userInfo/')

        response = session.get(url, headers=header)

        if response.status_code == 200 and 'json' in dir(response):
            resJSON = response.json()
            if 'id' in resJSON:
                return resJSON
            else:
                raise Exception('Invalid access token or token expired.')
        elif response.status_code == 403:
            raise PermissionDenied("permission denied ({url})")
        elif response.status_code == 500:
            return HttpResponseServerError(url)

    def get_client(self):
        """Provides authentication details to 'hs_restclient.HydroShare' and returns the object"""
        if self.auth_type == OAUTH_AC:
            token = self.get_token()
            auth = HydroShareAuthOAuth2(self.client_id, self.client_secret, token=token)
        elif self.auth_type == OAUTH_ROPC:
            auth = HydroShareAuthOAuth2(self.client_id, self.client_secret, username=self.username,
                                        password=self.password)
        else:
            raise InvalidGrantError("Invalid authorization grant type.")

        return HydroShareAdapter(auth=auth)

    @staticmethod
    def authorize_client(client_id, redirect_uri, response_type=None): # type: (str, str, str) -> None
        if response_type:
            auth = HSUOAuth(client_id, '__not_used__', redirect_uri=redirect_uri, response_type=response_type)
        else:
            auth = HSUOAuth(client_id, '__not_used__', redirect_uri=redirect_uri)

        url = auth._get_authorization_code_url()
        return redirect(url)

    @staticmethod
    def authorize_client_callback(client_id, client_secret, redirect_uri, code, response_type=None):
        # type: (str, str, str, str, str) -> HSUOAuth
        if response_type:
            auth = HSUOAuth(client_id, client_secret, redirect_uri=redirect_uri, response_type=response_type)
        else:
            auth = HSUOAuth(client_id, client_secret, redirect_uri=redirect_uri)

        json_token = auth._request_access_token(code)

        auth._set_token(**json_token)

        return auth

    def get_authorization_header(self):
        return {'Authorization': 'Bearer {access_token}'.format(access_token=self.access_token)}

    def _set_token(self, **token):
        for key, value in token.iteritems():
            if key in self.__dict__:
                setattr(self, key, value)
            else:
                logger.warning("skipped setting attribute '{attr}' on '{clsname}".format(attr=key, clsname=self.classname))

    def _refresh_authentication(self):
        """Does the same thing as 'get_client()', but attempts to refresh 'self.access_token' first"""
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

        return self.get_client()

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

    def _request_access_token(self, code):
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

        self.__auth_type__ = BASIC_AUTH

    @property
    def auth_type(self):
        return self.__auth_type__

    def get_user_info(self):
        # TODO: Implement...
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR)

    def get_client(self):
        auth = HydroShareAuthBasic(username=self.username, password=self.password)
        return HydroShareAdapter(auth=auth)

    def get_token(self):
        return None


class HSUAuthFactory(object):
    """
    Factory class for creating instances of 'HSUAuth'.

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
    @staticmethod
    def create(username=None, password=None, client_id=None, client_secret=None, token=None, redirect_uri=None,
               response_type=None):
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
            if response_type is None:
                response_type = DEFAULT_RESPONSE_TYPE

            implementation = HSUOAuth(client_id, client_secret, redirect_uri, response_type=response_type, **token)

        elif scheme == OAUTH_ROPC:
            implementation = HSUOAuth(client_id, client_secret, username=username, password=password)

        elif scheme == BASIC_AUTH:
            implementation = HSUBasicAuth(username, password)

        else:
            raise ValueError("Could not determine authentication scheme with provided parameters.")

        return HSUAuth(implementation)


__all__ = ["HSUAuth", "HSUOAuth", "HSUBasicAuth", "HSUAuthFactory"]
