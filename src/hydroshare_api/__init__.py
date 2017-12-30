from abc import ABCMeta, abstractmethod
import os
import re
import requests
from hs_restclient import HydroShare, HydroShareAuthOAuth2, HydroShareAuthBasic, \
    HydroShareException, HydroShareNotFound
from oauthlib.oauth2 import InvalidGrantError, InvalidClientError

class HydroShareUtilBaseClass(object):
    """The default base class for all HydroShareUtil classes"""
    pass


class HydroShareAuthBaseClass(HydroShareUtilBaseClass):
    """Base class for HydroShareUtil auth classes"""
    pass


class HydroShareAuthAbstractBaseClass(HydroShareAuthBaseClass):
    """Provides an interface to implement for classes using an authentication scheme (basic or oauth)"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def getUserInfo(self): pass

    @abstractmethod
    def authenticate(self): pass


class HydroShareAuthScheme(HydroShareAuthAbstractBaseClass):
    """Initializes variables needed for authentication"""
    def __init__(self):
        self._client_id = os.environ.get('HS_CLIENT_ID')
        self._client_secret = os.environ.get('HS_CLIENT_SECRET')
        self._redirect_uri = os.environ.get('HS_REDIRECT_URI')

    def getUserInfo(self):
        """Method is declared to satisfy implementation requirement of parent class"""
        raise NotImplementedError("Method should be implemented by a derived class of 'HydroShareAuthScheme'.")

    def authenticate(self):
        """Method is declared to satisfy implementation requirement of parent class"""
        raise NotImplementedError("Method should be implemented by a derived class of 'HydroShareAuthScheme'.")


class HydroShareAttributeError(ValueError):
    """Custom error class with a special "make-you-feel-good" message when you do something dumb"""
    def __init__(self, cls, attribute_name):
        arg = "'{attr}' is not a valid attribute name for '{clsname}'".format(
            attr=attribute_name, clsname=type(cls).__name__)
        super(HydroShareAttributeError, self).__init__(arg)


class HydroShareOAuth(HydroShareAuthScheme):
    """User authentication with OAuth 2.0 using the 'authorization_code' grant type"""
    _required_token_names = ['response_type', 'access_token', 'token_type', 'expires_in', 'refresh_token', 'scope']
    _allowed_schemes = ['https', 'http']
    _HS_BASE_URL_PROTO_WITH_PORT = '{scheme}://{hostname}:{port}/'
    _HS_BASE_URL_PROTO = '{scheme}://{hostname}/'
    _HS_API_URL_PROTO = '{base}hsapi/'
    _HS_TOKEN_URL_PROTO = '{base}o/'

    def __init__(self, scheme='https', hostname='www.hydroshare.org',
                 scope='read', port=None, token_type='Bearer',
                 response_type='authorization_code', **kwargs):
        super(HydroShareOAuth, self).__init__()

        self.token_type = token_type
        self.response_type = response_type
        self.scope = scope
        self.access_token = self.expires_in = self.refresh_token = None

        if scheme not in self._allowed_schemes:
            raise ValueError("{scheme} is not a valid scheme, must be 'https' or 'http'.".format(scheme=scheme))

        if port is None:
            self.base_url = self._HS_BASE_URL_PROTO.format(scheme=scheme, hostname=hostname)
        else:
            self.base_url = self._HS_BASE_URL_PROTO_WITH_PORT.format(scheme=scheme, port=port, hostname=hostname)

        self.api_url = self._HS_API_URL_PROTO.format(base=self.base_url)
        self.token_url = self._HS_TOKEN_URL_PROTO.format(base=self.base_url)

        for key, value in kwargs.iteritems():
            if key in self._required_token_names:
                setattr(self, key, value)
            else:
                raise HydroShareAttributeError(self, key)

        if self.access_token is None or self.expires_in is None or self.refresh_token is None:
            props = dir(self)
            missing_fields = [prop for prop in props if getattr(self, prop) is None and not re.search(r'^__[a-zA-Z0-9]+__$', prop)]
            classname = type(self).__name__
            fields = ", ".join(missing_fields)
            raise AttributeError("'{classname}' is missing required field(s): [{fields}]".format(
                classname=classname, fields=fields))

    def get_token(self):
        return {
            'response_type': self.response_type,
            'access_token': self.access_token,
            'token_type': self.token_type,
            'expires_in': self.expires_in,
            'refresh_token': self.refresh_token,
            'scope': self.scope
        }

    def get_user_info(self):
        # TODO: Implement...
        raise NotImplementedError("Method not implemented.")

    def authenticate(self):
        # TODO: Implement...
        raise NotImplementedError("Method not implemented.")


class HydroShareBasicAuth(HydroShareAuthScheme):
    """User authentication using 'Basic Auth' scheme."""
    def __init__(self, username, password):
        super(HydroShareBasicAuth, self).__init__()

        self.username = username
        self.password = password

    def getUserInfo(self):
        # TODO: Implement...
        raise NotImplementedError("Method not implemented.")

    def authenticate(self):
        # TODO: Implement...
        raise NotImplementedError("Method not implemented.")


class HydroShareAuthFactory(object):
    """
    This class provides a factory method for creating instances of 'HydroShareAuth'.

    'HydroShareAuth' has a required 'auth' paramater, which is an instance of either 'HydroShareBasicAuth' or
    'HydroShareOAuth'.

    Example: Creating a 'HydroShareAuth' object using the 'basic' authentication scheme:
        hsauth = HydroShareAuthFactory.factory(HydroShareBasicAuth, username="<your_username>", password="<your_password>")

    Example of creating a 'HydroShareAuth' object using the 'OAuth 2.0' authentication scheme:
        hsauth = HydroShareAuthFactory.factory(HydroShareOAuth,
                                               access_token="<your_access_token>",
                                               expires_in=3600,
                                               refresh_token="<your_refresh_token>")
    """
    def __init__(self):
        raise NotImplementedError("'__init__' is not implemented. Use the static method \
        'HydroShareAuthFactory.factory(...)' to create an instance of 'HydroShareAuth' instead.")

    @staticmethod
    def factory(cls, *args, **kwargs):
        class HydroShareAuth(HydroShareAuthBaseClass):
            def __init__(self, auth):
                self.auth = auth
                self.session = None
                self.initialize_session()

            def initialize_session(self):
                self.session = requests.Session()
                token = getattr(self.auth, 'access_token')
                token_type = getattr(self.auth, 'token_type')
                if token and token_type:
                    self.session.headers = {'Authorization': '{token_type} {token}'.format(token_type=token_type, token=token)}

        if isinstance(cls, HydroShareAuthAbstractBaseClass):
            cls = cls.__name__

        if cls not in [cls.__name__ for cls in [HydroShareBasicAuth, HydroShareOAuth]]:
            raise ValueError("'{cls}' is not a valid class".format(cls=cls))
        if cls is HydroShareBasicAuth.__name__:
            return HydroShareAuth(auth=HydroShareBasicAuth(*args))
        if cls is HydroShareOAuth.__name__:

            return HydroShareAuth(auth=HydroShareOAuth(kwargs))


class HydroShareAccount(HydroShareUtilBaseClass):
    _field_names = ['id', 'email', 'first_name', 'last_name', 'organization', 'username']
    def __init__(self, **kwargs):
        self.id = None
        self.email = None
        self.first_name = None
        self.last_name = None
        self.organization = None
        self.username = None

        props = dir(self)
        for key, value in kwargs.iteritems():
            if key in props:
                setattr(self, key, value)
            else:
                raise HydroShareAttributeError(self, key)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'organization': self.organization,
            'username': self.username
        }

    def __repr__(self):
        return "<{classname}: {username}>".format(classname=type(self).__name__, username=self.username)
