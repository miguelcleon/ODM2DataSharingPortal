from abc import ABCMeta, abstractmethod
import os
import re
import requests
from copy import deepcopy
from hs_restclient import HydroShare, HydroShareAuthOAuth2, HydroShareAuthBasic, \
    HydroShareException, HydroShareNotFound
from oauthlib.oauth2 import InvalidGrantError, InvalidClientError

NOT_IMPLEMENTED_ERROR = "Method not implemeneted."


class HydroShareUtilityBaseClass(object):
    """The base class for all HSU* classes"""

    @property
    def classname(self):
        return self.__class__.__name__

    def __iter__(self):
        for attr, value in self.__dict__.iteritmes():
            yield attr, value

    def get_metadata(self):
        copy = {}
        for key, value in self:
            if value is None:
                copy[key] = ""
            else:
                copy[key] = value
        return copy


class HSUAttributeError(ValueError):
    """Custom error class that uses a special message format for when you do something dumb"""

    def __init__(self, cls, attribute_name):
        arg = "'{attr}' is not a valid attribute name for '{clsname}'".format(
            attr=attribute_name, clsname=type(cls).__name__)
        super(HSUAttributeError, self).__init__(arg)
