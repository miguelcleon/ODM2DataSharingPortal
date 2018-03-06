# adapter.py
import requests
from hs_restclient import HydroShare, DEFAULT_HOSTNAME, HydroShareNotAuthorized, HydroShareNotFound, \
    HydroShareHTTPException


class HydroShareAdapter(HydroShare):
    def __init__(self, hostname=DEFAULT_HOSTNAME, port=None, use_https=True, verify=True,
                 auth=None, default_headers=None):
        self._default_headers = default_headers
        super(HydroShareAdapter, self).__init__(hostname=hostname, port=port, use_https=use_https, verify=verify,
                                                auth=auth)

    def _build_params(self, params):  # type: (dict) -> str
        param_vals = ['{param}={val}'.format(param=p, val=v) for p, v in params.iteritems()]
        return "?{params}".format(params="&".join(param_vals))

    def _request(self, method, url, params=None, data=None, files=None, headers=None, stream=False, **kwargs):

        timeout = None
        if 'timeout' in kwargs:
            timeout = kwargs.get('timeout', None)

        if self._default_headers and headers:
            headers = headers
            headers.update(self._default_headers)
        elif self._default_headers:
            headers = self._default_headers

        try:
            request = self.session.request(method, url, params=params, data=data, files=files, headers=headers,
                                           stream=stream, verify=self.verify, timeout=timeout)
        except requests.ConnectionError:
            self._initializeSession()
            request = self.session.request(method, url, params=params, data=data, files=files, headers=headers,
                                           stream=stream, verify=self.verify, timeout=timeout)
        return request

    def getSystemMetadata(self, pid, **kwargs):
        """
        Returns system metadata for a resource which includes the dublin core elements
        Note: HydroShareAdapter overrides it's super class method, getSystemMetadata(), so 'timeout' can be
        included in **kwargs. By default, the requests library does not have timeout limit for HTTP requests, and
        some views wait for getSystemMetadata() to complete an HTTP request to hydroshare.org before the views are
        rendered.
        """
        timeout = None
        if 'timeout' in kwargs:
            timeout = kwargs.get('timeout', None)

        url = "{url_base}/resource/{pid}/sysmeta/".format(url_base=self.url_base,
                                                          pid=pid)
        headers = self._default_headers

        access_token = self.auth.token.get('access_token', None)
        if access_token is not None:
            headers['Authorization'] = 'Bearer {0}'.format(access_token)

        req = requests.get(url, headers=headers, timeout=timeout)
        if req.status_code != 200:
            if req.status_code == 403:
                raise HydroShareNotAuthorized((req.request.method, url))
            elif req.status_code == 404:
                raise HydroShareNotFound((pid,))
            else:
                raise HydroShareHTTPException((url, req.request.method, req.status_code))

        return req.json()
