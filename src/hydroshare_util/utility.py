import re
from . import HydroShareUtilityBaseClass
from auth import AuthUtil
from adapter import HydroShareAdapter
from resource import Resource
import logging
import json
import time

class HydroShareUtility(HydroShareUtilityBaseClass):
    """Utility class for accessing and consuming HydroShare's REST API."""
    RE_PERIOD = re.compile(r'(?P<tag_start>^start=)(?P<start>[0-9-]{10}T[0-9:]{8}).{2}(?P<tag_end>end=)'
                           r'(?P<end>[0-9-]{10}T[0-9:]{8}).{2}(?P<tag_scheme>scheme=)(?P<scheme>.+$)', re.I)
    XML_NS = {'dc': "http://purl.org/dc/elements/1.1/",
              'dcterms': "http://purl.org/dc/terms/",
              'hsterms': "http://hydroshare.org/terms/",
              'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
              'rdfs1': "http://www.w3.org/2001/01/rdf-schema#"}
    XML_COVERAGE_PROTO = "start={start}; end={end}; scheme=W3C-DTF"
    TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

    def __init__(self, auth=None): # type: (AuthUtil) -> None
        self.auth = auth

    @property
    def client(self):
        if isinstance(self.auth, AuthUtil):
            return self.auth.get_client()
        else:
            return HydroShareAdapter()

    def get_resources(self):
        """
        Gets a list of all resources. Warning: This takes a long time to complete
        :return: Resource[]
        """

        resources = list()
        start_time = time.time()

        logging.info("Grabbing resources from www.hydroshare.org:")

        for resource_json in self.client.resources():
            logging.info(json.dumps(resource_json))
            resource = Resource(self.client, **resource_json)
            resources.append(resource)

        elapsed_time = time.time() - start_time
        et_string = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        logging.info("Total time to get HydroShare resources: {time}".format(time=et_string))

        return resources

    def get_resource_metadata(self, pid):
        data = self.client.get_resource_metadata(pid)
        logging.info("Fetched resource metadata: {json_data}".format(json_data=json.dumps(data)))
        return Resource(self.client, **data)

    def get_user_info(self):
        try:
            return self.client.get_user_info()
        except Exception:
            return None

    def get_resource_types(self):
        try:
            Resource.RESOURCE_TYPES = [type for type in self.client.get_resource_types()]
        except Exception as e:
            logging.error("Failed to get resource types!\n{error}".format(error=e))


__all__ = ["HydroShareUtility"]
