# adapter.py
from hs_restclient import HydroShare, DEFAULT_HOSTNAME, HydroShareNotAuthorized, HydroShareNotFound, \
    HydroShareHTTPException


class HydroShareAdapter(HydroShare):
    def __init__(self, hostname=DEFAULT_HOSTNAME, port=None, use_https=True, verify=True,
                 auth=None, default_headers=None):
        self._default_headers = default_headers
        super(HydroShareAdapter, self).__init__(hostname=hostname, port=port, use_https=use_https, verify=verify, auth=auth)

    def _build_params(self, params): # type: (dict) -> str
        param_vals = ['{param}={val}'.format(param=p, val=v) for p, v in params.iteritems()]
        return "?{params}".format(params="&".join(param_vals))

    def _request(self, method, url, params=None, data=None, files=None, headers=None, stream=False):
        _headers = None
        if self._default_headers and headers:
            _headers = headers
            _headers.update(self._default_headers)
        elif self._default_headers:
            _headers = self._default_headers

        return super(HydroShareAdapter, self)._request(method, url, params=params, data=data, files=files, stream=stream, headers=_headers)

    def get_resource_list(self, **kwargs):
        return self.getResourceList(**kwargs)

    def get_system_metadata(self, pid):
        return self.getSystemMetadata(pid)

    def get_science_metadata_RDF(self, pid):
        return self.getScienceMetadata(pid)

    def get_science_metadata(self, pid):
        return self.getScienceMetadata(pid)

    def update_science_metadata(self, pid, metadata):
        return self.updateScienceMetadata(pid, metadata)

    def get_resource_map(self, pid):
        return self.getResourceMap(pid)

    def get_resource(self, pid, destination=None, unzip=False, wait_for_bag_creation=True):
        return self.getResource(pid, destination=destination, unzip=unzip, wait_for_bag_creation=wait_for_bag_creation)

    def get_resource_metadata(self, pid):
        return self.get_system_metadata(pid)

    def get_resource_types(self):
        return self.getResourceTypes()

    def create_resource(self, resource_type, title, resource_file=None, resource_filename=None,
                       abstract=None, keywords=None,
                       edit_users=None, view_users=None, edit_groups=None, view_groups=None,
                       metadata=None, extra_metadata=None, progress_callback=None):
        return self.createResource(resource_type, title, resource_file=resource_file,
                                   resource_filename=resource_filename, abstract=abstract, keywords=keywords,
                                   edit_users=edit_users, view_users=view_users, edit_groups=edit_groups,
                                   view_groups=view_groups, metadata=metadata, extra_metadata=extra_metadata,
                                   progress_callback=progress_callback)

    def delete_resource(self, pid):
        return self.deleteResource(pid)

    def set_access_rules(self, pid, public=False):
        return self.setAccessRules(pid, public=public)

    def add_resource_file(self, pid, resource_file, resource_filename=None, progress_callback=None):
        return self.addResourceFile(pid, resource_file, resource_filename=resource_filename,
                                    progress_callback=progress_callback)

    def get_resource_file(self, pid, filename, destination=None):
        return self.getResourceFile(pid, filename, destination=destination)

    def delete_resource_file(self, pid, filename):
        return self.deleteResourceFile(pid, filename)

    def get_resource_file_list(self, pid):
        return self.getResourceFileList(pid)

    def get_resource_folder_contents(self, pid, pathname):
        return self.getResourceFolderContents(pid, pathname)

    def create_resource_folder(self, pid, pathname):
        return self.createResourceFolder(pid, pathname)

    def delete_resource_folder(self, pid, pathname):
        return self.deleteResourceFolder(pid, pathname)

    def get_user_info(self):
        return self.getUserInfo()
