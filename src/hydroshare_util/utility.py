import re
import os
from . import HydroShareUtilityBaseClass, NOT_IMPLEMENTED_ERROR
from hs_restclient import HydroShare, HydroShareAuthBasic, HydroShareAuthOAuth2, HydroShareHTTPException
from auth import OAUTH_AC, OAuthUtil

class HydroShareUtility(HydroShareUtilityBaseClass):
    """
    Utility class for accessing and consuming HydroShare's REST API.

    Before HydroShareUtility can begin consuming the API, a user needs to be authenticated. This is done by calling
    'connect(...)' and providing the necessary parameters depending on the type of authentication. After the connect()
    method has been called, you can use self.client to access the API.
    """
    def __init__(self, auth=None, time_format="%Y-%m-%dT%H:%M:%S", xml_coverage="start={start}; end={end}; scheme=W3C-DTF"):
        self.auth = auth  # type: HydroShare
        self.RE_PERIOD = re.compile(r'(?P<tag_start>^start=)(?P<start>[0-9-]{10}T[0-9:]{8}).{2}(?P<tag_end>end=)'
                                    r'(?P<end>[0-9-]{10}T[0-9:]{8}).{2}(?P<tag_scheme>scheme=)(?P<scheme>.+$)', re.I)
        self.XML_NS = {'dc': "http://purl.org/dc/elements/1.1/",
                       'dcterms': "http://purl.org/dc/terms/",
                       'hsterms': "http://hydroshare.org/terms/",
                       'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                       'rdfs1': "http://www.w3.org/2001/01/rdf-schema#"}
        self.TIME_FORMAT = time_format
        self.XML_COVERAGE_PROTO = xml_coverage

    @staticmethod
    def get_resources():
        pass

    def get_resource_file_list(self, resource_id):
        try:
            return list(self.auth.getResourceFileList(resource_id))
        except Exception as e:
            print 'Error while fetching resource files {}'.format(e)
            return []

    def get_resource(self):
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

    def get_user_info(self):
        client = self.auth.get_client()
        if self.auth.auth_type == OAUTH_AC:
            imp = self.auth.__implementation
            header = imp.get_authorization_header() if isinstance(imp, OAuthUtil) else None
            return client.get_user_info(headers=header)
        else:
            return client.get_user_info()


__all__ = ["HydroShareUtility"]
