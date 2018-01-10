import re
from . import HydroShareUtilityBaseClass
from auth import AuthUtil
from adapter import HydroShareAdapter
from resource import Resource

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

    def __init__(self, auth): # type: (AuthUtil, str, str) -> None
        self.auth = auth

    @staticmethod
    def get_resources():
        hs = HydroShareAdapter()
        resources = list()
        for resource in hs.resources():
            print resource
            resources.append(resource)
        return resources


__all__ = ["HydroShareUtility"]
