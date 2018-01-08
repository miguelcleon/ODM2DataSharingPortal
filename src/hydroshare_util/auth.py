from abc import ABCMeta, abstractmethod, abstractproperty
from enum import Enum
import re
import requests
import logging as logger
from oauthlib.oauth2 import InvalidGrantError
from hs_restclient import HydroShareAuthOAuth2, HydroShareAuthBasic
from adapter import HydroShareAdapter
from . import HydroShareUtilityBaseClass, ImproperlyConfiguredError, NOT_IMPLEMENTED_ERROR
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseServerError
from django.conf import settings

OAUTH_ROPC = 'oauth-resource-owner-password-credentials'
OAUTH_AC = 'oauth-authorization-code'
BASIC_AUTH = 'basic'


class AuthUtil(HydroShareUtilityBaseClass):
    """Main authentication class. Use 'AuthUtilFactory' to create instances of this class."""
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
    def authorize_client(response_type=None):
        return OAuthUtil.authorize_client(response_type=response_type)

    @staticmethod
    def authorize_client_callback(code):
        oauth = OAuthUtil.authorize_client_callback(code)
        auth = AuthUtil(oauth)
        return auth

    @staticmethod
    def authorize(scheme, username=None, password=None, token=None):
        return AuthUtilFactory.create(scheme, username=username, password=password, token=token)


class AuthUtilImplementor(HydroShareUtilityBaseClass):
    """Defines bridging interface for implementation classes of 'AuthUtil'"""
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


class OAuthUtil(AuthUtilImplementor):
    """User authentication with OAuth 2.0 using the 'authorization_code' grant type"""
    _required_token_fields = ['response_type', 'access_token', 'token_type', 'expires_in', 'refresh_token', 'scope']
    _HS_BASE_URL_PROTO_WITH_PORT = '{scheme}://{hostname}:{port}/'
    _HS_BASE_URL_PROTO = '{scheme}://{hostname}/'
    _HS_API_URL_PROTO = '{base}hsapi/'
    _HS_OAUTH_URL_PROTO = '{base}o/'

    @property
    def auth_type(self):
        return self._authorization_grant_type

    def __init__(self, redirect_uri=None, use_https=True, hostname='www.hydroshare.org',
                 port=None, scope=None, access_token=None, refresh_token=None, expires_in=None, token_type='Bearer',
                 response_type='code', username=None, password=None, **kwargs):

        self.__redirect_uri__ = redirect_uri
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

        if settings.HYDROSHARE_UTIL_CONFIG:
            self.__client_id = settings.HYDROSHARE_UTIL_CONFIG['CLIENT_ID']
            self.__client_secret = settings.HYDROSHARE_UTIL_CONFIG['CLIENT_SECRET']
            self.__redirect_uri = settings.HYDROSHARE_UTIL_CONFIG['REDIRECT_URI']
        else:
            raise ImproperlyConfiguredError()

        for key, value in kwargs.iteritems():
            if key in self.__dict__:
                setattr(self, key, value)

        if self.username and self.password:
            self._authorization_grant_type = OAUTH_ROPC
        else:
            self._authorization_grant_type = OAUTH_AC

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

        header = self.get_authorization_header()
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
            auth = HydroShareAuthOAuth2(self.__client_id, self.__client_secret, token=token)
        elif self.auth_type == OAUTH_ROPC:
            auth = HydroShareAuthOAuth2(self.__client_id, self.__client_secret, username=self.username,
                                        password=self.password)
        else:
            raise InvalidGrantError("Invalid authorization grant type.")

        header = self.get_authorization_header()
        return HydroShareAdapter(auth=auth, auth_header=header)

    @staticmethod
    def authorize_client(response_type=None): # type: (str, str, str) -> None
        if response_type:
            auth = OAuthUtil(response_type=response_type)
        else:
            auth = OAuthUtil()

        url = auth._get_authorization_code_url()
        return redirect(url)

    @staticmethod
    def authorize_client_callback(code, response_type=None):
        # type: (str, str) -> dict
        redirect_uri = settings.HYDROSHARE_UTIL_CONFIG['REDIRECT_URI']

        if response_type:
            auth = OAuthUtil(redirect_uri=redirect_uri, response_type=response_type)
        else:
            auth = OAuthUtil(redirect_uri=redirect_uri)

        token = auth._request_access_token(code)

        return token

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
            'client_id': self.__client_id,
            'client_secret': self.__client_secret,
            'redirect_uri': self.__redirect_uri,
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
            'client_id': self.__client_id,
            'redirect_uri': self.__redirect_uri
        }

        return self._build_oauth_url('authorize/', params)

    def _get_access_token_url(self, code):
        params = {
            'grant_type': 'authorization_code',
            'client_id': self.__client_id,
            'client_secret': self.__client_secret,
            '__redirect_uri': self.__redirect_uri,
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


class BasicAuthUtil(AuthUtilImplementor):
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


class AuthUtilFactory(object):
    """
    Factory class for creating instances of 'AuthUtil'.

    Example: Creating a 'AuthUtil' object using the 'basic' authentication scheme:
        hsauth = AuthUtilFactory.create(username='<your username>', password='<your password>')

    Example of creating a 'AuthUtil' object using the 'oauth' authentication scheme and client credential grant type:
        hsauth = AuthUtilFactory.create(username='<your_username>', password='<your_password>',
                                        client_id='<__client_id>', client_secret='<__client_secret>')

    Example of creating an 'AuthUtil' object using the 'auth' authentication scheme and authorization code grant type:
        token = get_token() # get_token is a stand for getting a token dictionary
        hsauth = AuthUtilFactory.create(client_id='<__client_id>', client_secret='<__client_secret>',
                                        token=token, __redirect_uri='<your_app_redirect_uri>')
    """
    @staticmethod
    def create(scheme, username=None, password=None, token=None):
        # type: (AuthScheme, str, str, dict, str) -> AuthUtil
        """
        Factory method creates and returns an instance of AuthUtil. The chosen scheme ('basic' or 'oauth') determines
        the background implementation. The following table shows which parameters are required for each type of
        authentication scheme.

        +--------------------------------------------------------------+
        |       scheme type      |  username  |  password  |   token   |
        +------------------------+-------------------------------------+
        | Basic Auth             |     X      |     X      |           |
        +------------------------+-------------------------------------+
        | OAuth with credentials |     X      |     X      |           |
        +------------------------+-------------------------------------+
        | OAuth with token       |            |            |     X     |
        +------------------------+--------------------------------------

        :param scheme: The authentication scheme, either 'basic' or 'oauth'
        :param username: user's username
        :param password: user's password
        :param token: a dictionary containing values for 'access_token', 'token_type', 'refresh_token', 'expires_in',
        and 'scope'
        """
        if scheme == AuthScheme.OAUTH and token:

            implementation = OAuthUtil(**token)

        elif scheme == AuthScheme.OAUTH and username and password:

            implementation = OAuthUtil(username=username, password=password)

        elif scheme == AuthScheme.BASIC and username and password:

            implementation = BasicAuthUtil(username, password)

        else:
            raise ValueError("incorrect arguments supplied to 'AuthUtilFactory.create()' using authentication scheme \
                '{scheme}'".format(scheme=scheme))

        return AuthUtil(implementation)


class AuthScheme(Enum):
    BASIC = 'basic'
    OAUTH = 'oauth'


__all__ = ["AuthUtil", "OAuthUtil", "BasicAuthUtil", "AuthUtilFactory", "AuthScheme"]
