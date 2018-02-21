"""

Utility library for consuming HydroShare's REST API.

Built on top of the 'hs_restclient' library.

"""
from hs_restclient import HydroShareNotFound, HydroShareHTTPException

__title__ = 'hydroshare_util'
__version__ = '1.0'

NOT_IMPLEMENTED_ERROR = "Method not implemeneted."


class HydroShareUtilityBaseClass(object):
    """The base class for all HSU* classes"""

    @property
    def classname(self):
        return self.__class__.__name__

    def __iter__(self):
        for attr, value in self.__dict__.iteritems():
            yield attr, value

    def to_object(self, clean=False):
        copy = {}
        for key, value in self:
            if clean is True and value is not None:
                if (isinstance(value, str) or getattr(value, '__iter__', None)) and len(value) > 0:
                    copy[key] = value
            elif not clean:
                copy[key] = value
        return copy


class HSUClassAttributeError(ValueError):
    """Custom error class that uses a special message format for when you do something dumb"""

    def __init__(self, cls, attribute_name):
        arg = "'{attr}' is not a valid attribute name for '{clsname}'".format(
            attr=attribute_name, clsname=type(cls).__name__)
        super(HSUClassAttributeError, self).__init__(arg)


class HSUOAuthCredentialsTypeError(TypeError):
    def __init__(self, username, password, token):
        is_resource_owner_password_credential_err = (username or password) and not token
        is_authorization_code_err = not (username and password and token)

        if is_resource_owner_password_credential_err:
            arg = "'username' or 'password' cannot be a 'NoneType' object when using OAuth Resource Owner Password \
                    Credential grant type."
        elif is_authorization_code_err:
            arg = "'token' cannot be a 'NonType' object when using OAuth Authorization Code grant type."
        else:
            arg = "cannot use 'NoneType' objects to authorize client. You must provide a username and password, or you \
                    must provide a token."

        super(HSUOAuthCredentialsTypeError, self).__init__(arg)


class NotAuthorizedError(Exception):
    def __init__(self, *args, **kwargs): # real signature unknown
        super(NotAuthorizedError, self).__init__(args, kwargs)


class ImproperlyConfiguredError(Exception):
    def __init__(self, **kwargs):
        arg = "'hydroshare_util' improperly configured. Please refer to the documentation \
        (https://github.com/ODM2/ODM2WebSDL/tree/hydroshare/src/hydroshare_util)"
        super(ImproperlyConfiguredError, self).__init__(arg, kwargs)


__all__ = ["HSUClassAttributeError", "HSUOAuthCredentialsTypeError", "NotAuthorizedError", "HydroShareNotFound",
           "HydroShareHTTPException"]
