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
    XML_COVERAGE_PROTO = "start={start}; end={end}; scheme=W3C-DTF"

    def __init__(self, auth=None):  # type: (AuthUtil) -> None
        self.auth = auth
        # self.request_resource_types()

    @property
    def client(self):
        if isinstance(self.auth, AuthUtil):
            return self.auth.get_client()
        else:
            return HydroShareAdapter()

    def get_resources(self, limit=None, owner=None):
        """
        Gets a list of all resources. Warning: This takes a long time to complete
        :return: Resource[]
        """

        resources = list()
        start_time = time.time()

        logging.info("Grabbing {limit} resources from www.hydroshare.org:".format(limit=limit if limit else ''))

        for resource_json in self.client.resources(owner=owner):
            if isinstance(limit, int):
                limit -= 1
            elif isinstance(limit, int) and limit < 1:
                break

            logging.info(json.dumps(resource_json))
            resource = Resource(self.client, raw=resource_json, **resource_json)
            resources.append(resource)

        elapsed_time = time.time() - start_time
        et_string = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        logging.info("Total time to get HydroShare resources: {time}".format(time=et_string))

        return resources

    def get_resource_system_metadata(self, pid):
        data = self.client.get_system_metadata(pid)
        logging.info("Fetched resource metadata: {json_data}".format(json_data=json.dumps(data)))
        return Resource(self.client, **data)

    def get_user_info(self):
        try:
            return self.client.getUserInfo()
        except Exception as e:
            logging.error(e)
        return None

    def request_resource_types(self):
        from multiprocessing import Process
        proc = Process(target=self._request_resource_types_async)
        proc.start()
        proc.join()

    def _request_resource_types_async(self):
        try:
            Resource.RESOURCE_TYPES = [type_ for type_ in self.client.getResourceTypes()]
        except Exception as e:
            logging.error("Failed to get resource types.\n\t{error}".format(error=e))


__all__ = ["HydroShareUtility"]
