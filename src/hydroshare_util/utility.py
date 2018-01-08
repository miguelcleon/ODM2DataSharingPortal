import re
from . import HydroShareUtilityBaseClass
from auth import AuthUtil
from adapter import HydroShareAdapter

class HydroShareUtility(HydroShareUtilityBaseClass):
    """Utility class for accessing and consuming HydroShare's REST API."""
    def __init__(self, auth=None, time_format="%Y-%m-%dT%H:%M:%S", xml_coverage="start={start}; end={end}; scheme=W3C-DTF"):
        # type: (AuthUtil, str, str) -> None
        self.auth = auth
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


__all__ = ["HydroShareUtility"]
