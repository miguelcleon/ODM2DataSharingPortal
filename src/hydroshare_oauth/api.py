from os import environ as env
import requests
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.shortcuts import HttpResponseRedirect

class HydroShareAPI():

    _API_URL_BASE = 'https://www.hydroshare.org/hsapi/'
    _OAUTH_URL_BASE = 'https://www.hydroshare.org/o/'

    _client_id = env.get('HS_CLIENT_ID')
    _client_secret = env.get('HS_CLIENT_SECRET')
    _response_type = env.get('HS_RESPONSE_TYPE')
    _redirect_uri = env.get('HS_REDIRECT_URI')

    @staticmethod
    def get_auth_code_url():
        params = {
            'response_type': HydroShareAPI._response_type,
            'client_id': HydroShareAPI._client_id,
            'redirect_uri': HydroShareAPI._redirect_uri
        }
        return HydroShareAPI.build_oauth_url('authorize/', params)

    @staticmethod
    def get_refresh_code_params(refresh_token):
        return {
            'grant_type': 'refresh_token',
            'client_id': HydroShareAPI._client_id,
            'client_secret': HydroShareAPI._client_secret,
            'refresh_token': refresh_token,
            'redirect_uri': HydroShareAPI._redirect_uri,
        }

    @staticmethod
    def build_oauth_url(path, params):
        url_params = []
        for key, value in params.iteritems():
            url_params.append('{0}={1}'.format(key, value))
        return "{url_base}{path}?{params}".format(url_base=HydroShareAPI._OAUTH_URL_BASE, path=path, params='&'.join(url_params))

    @staticmethod
    def get_access_token(code):
        params = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': HydroShareAPI._client_id,
            'client_secret': HydroShareAPI._client_secret,
            'redirect_uri': HydroShareAPI._redirect_uri
        }
        url = HydroShareAPI.build_oauth_url('token/', params)
        res = requests.post(url)

        if res.status_code == 200:
            resJSON = res.json()
            if 'access_token' in resJSON:
                user_info = HydroShareAPI.get_user_info(resJSON['access_token'])
                return HydroShareAuth(res.json(), user_info)
            else:
                return None
        else:
            return None

    @staticmethod
    def authorize_client():
        return HttpResponseRedirect(reverse('hydroshare_oauth:oauth_redirect'))

    @staticmethod
    def get_auth_header(token):
        return { 'Authorization': 'Bearer {token}'.format(token=token) }

    @staticmethod
    def get_user_info(token):
        session = requests.Session()
        header = HydroShareAPI.get_auth_header(token)
        response = session.get("{url_base}{path}".format(url_base=HydroShareAPI._API_URL_BASE, path='userInfo/'), headers=header)

        if response.status_code == 200 and 'json' in dir(response):
            resJSON = response.json()
            if 'id' in resJSON:
                return resJSON
            else:
                raise Exception('Invalid access token or token expired.')
        elif response.status_code == 403:
            raise Exception('Not Authorized')
        else:
            raise Exception('Something broke...')

    # TODO: Implement method
    def refresh_token(self, hsuser):
        pass


class HydroShareAuth():
    def __init__(self, auth, user_info=None):
        self.access_token = auth['access_token']
        self.refresh_token = auth['refresh_token']
        self.expires_in = auth['expires_in']
        self.scope = auth['scope']
        if user_info:
            self.user_info = HydroShareUserInfo(user_info)


class HydroShareUserInfo():
    def __init__(self, info):
        self.id = info['id']
        self.email = info['email']
        self.first_name = info['first_name']
        self.last_name = info['last_name']
        self.organization = info['organization']
        self.username = info['username']
