import re
from . import _HydroShareUtilityBaseClass, NOT_IMPLEMENTED_ERROR, HSUOAuthCredentialsTypeError
from .Auth import HSUAuthFactory, HSUAuth
from enum import Enum

class AuthScheme(Enum):
    BASIC = 'basic'
    OAUTH = 'oauth'


class HydroShareUtility(_HydroShareUtilityBaseClass):
    """
    Utility class for accessing and consuming HydroShare's REST API.

    Before HydroShareUtility can begin consuming the API, a user needs to be authenticated. This is done by calling
    'connect(...)' and providing the necessary parameters depending on the type of authentication. After the connect()
    method has been called, you can use self.client to access the API.
    """
    def __init__(self, time_format="%Y-%m-%dT%H:%M:%S", xml_coverage="start={start}; end={end}; scheme=W3C-DTF"):
        self.client = None
        self.RE_PERIOD = re.compile(r'(?P<tag_start>^start=)(?P<start>[0-9-]{10}T[0-9:]{8}).{2}(?P<tag_end>end=)'
                                    r'(?P<end>[0-9-]{10}T[0-9:]{8}).{2}(?P<tag_scheme>scheme=)(?P<scheme>.+$)', re.I)
        self.XML_NS = {'dc': "http://purl.org/dc/elements/1.1/",
                       'dcterms': "http://purl.org/dc/terms/",
                       'hsterms': "http://hydroshare.org/terms/",
                       'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                       'rdfs1': "http://www.w3.org/2001/01/rdf-schema#"}
        self.TIME_FORMAT = time_format
        self.XML_COVERAGE_PROTO = xml_coverage

    def connect(self, scheme, username=None, password=None, token=None, client_id=None, client_secret=None): # type: (str, str, str, dict, str, str) -> None
        if scheme == AuthScheme.BASIC:
            auth_util = HSUAuthFactory.create(username=username, password=password)
        elif scheme == AuthScheme.OAUTH:

            if username and password:
                auth_util = HSUAuthFactory.create(username=username, password=password, client_id=client_id,
                                                  client_secret=client_secret)
            elif token:
                auth_util = HSUAuthFactory.create(client_id=client_id, client_secret=client_secret, token=token)
            else:
                raise HSUOAuthCredentialsTypeError(username, password, token)
        else:
            raise ValueError("'{scheme}' is not a valid authentication scheme, must be 'basic' or 'oauth'".format(scheme=scheme))

        self.client = auth_util.authenticate()

    def purge_duplicate_gamut_file(self, resource_id, regex, conmmit_delete=False):
        """
        Removes all files that have a duplicate-style naming pattern (e.g. ' (1).csv', '_ASDFGJK9.csv'
        :param resource_id: Resource to inspect for duplicates
        :type resource_id: Resource object received from the HydroShare API client
        :param confirm_delete: If true, requires input that confirm file should be deleted
        :type confirm_delete: bool
        """
        re_breakdown = re.compile(regex, re.I)
        resource_files = self.get_resource_file_list(resource_id)
        duplicates_list = []
        for remote_file in resource_files:
            results = re_breakdown.match(remote_file['url'])  # Check the file URL for expected patterns
            temp_dict = {'duplicated': ''} if results is None else results.groupdict()  # type: dict
            if len(temp_dict['duplicated']) > 0:  # A non-duplicated file will match with length 0
                duplicates_list.append(temp_dict)  # Save the file name so we can remove it later

        for file_detail in duplicates_list:
            if conmmit_delete:
                self.client.deleteResourceFile(resource_id, file_detail['name'])
                print('Deleting file {}...'.format(file_detail['name']))
            else:
                user_answer = raw_input("Delete file {} [Y/n]: ".format(file_detail['name']))
                if user_answer.lower() == 'n':
                    print('Skipping duplicate file {}...'.format(file_detail['name']))
                else:
                    self.client.deleteResourceFile(resource_id, file_detail['name'])

    def get_resource_file_list(self, resource_id):
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR)

    def get_resources(self, resource):
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR)

    def get_metadata_for_resource(self, resource):
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR)

    def update_resource_metadata(self, resource):
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR)

    def get_file_by_resource_id(self, resource_id):
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR)

    def get_file_list_for_resource(self, resource):
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR)

    def filter_resources(self, regex_string, regex_flags=None, owner=None):
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR)

    def upload_files(self, files, resource_id):
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR)

    def set_resources_as_public(self, resource_ids):
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR)

    def get_resource_coverage_period(self, resource_id):
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR)

    def delete_files_in_resource(self, resource_id):
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR)

    def create_resource(self, resource):
        raise NotImplementedError(NOT_IMPLEMENTED_ERROR)


__all__ = ["AuthScheme", "HydroShareUtility"]