from os import environ as env
import requests
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseServerError
from django.core.urlresolvers import reverse
from django.shortcuts import HttpResponseRedirect
from django.http import HttpResponseNotFound
from oauthlib.oauth2 import TokenExpiredError
from hs_restclient import HydroShare, HydroShareAuthOAuth2

class HydroShareAPI():

    _API_URL_BASE = 'https://www.hydroshare.org/hsapi/'
    _OAUTH_URL_BASE = 'https://www.hydroshare.org/o/'

    __client_id = env.get('HS_CLIENT_ID')
    __client_secret = env.get('HS_CLIENT_SECRET')
    __response_type = env.get('HS_RESPONSE_TYPE')
    __redirect_uri = env.get('HS_REDIRECT_URI')

    @staticmethod
    def get_auth_code_url():
        params = {
            'response_type': HydroShareAPI.__response_type,
            'client_id': HydroShareAPI.__client_id,
            'redirect_uri': HydroShareAPI.__redirect_uri
        }
        return HydroShareAPI.build_oauth_url('authorize/', params)

    @staticmethod
    def get_refresh_code_params(refresh_token):
        return {
            'grant_type': 'refresh_token',
            'client_id': HydroShareAPI.__client_id,
            'client_secret': HydroShareAPI.__client_secret,
            'redirect_uri': HydroShareAPI.__redirect_uri,
            'refresh_token': refresh_token
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
            'client_id': HydroShareAPI.__client_id,
            'client_secret': HydroShareAPI.__client_secret,
            'redirect_uri': HydroShareAPI.__redirect_uri,
            'code': code
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
        return HttpResponseRedirect(reverse('hydroshare_api:oauth_redirect'))

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
            raise PermissionDenied
        else:
            return HttpResponseServerError()

    # TODO: Implement method
    @staticmethod
    def refresh_token(hsaccount):
        raise Exception('method not implemented.')

    @staticmethod
    def get_resources(hsaccount):
        client_id = HydroShareAPI.__client_id
        client_secret = HydroShareAPI.__client_secret
        token = hsaccount.get_token()
        auth = HydroShareAuthOAuth2(client_id=client_id, client_secret=client_secret, token=token)

        try:
            hs = HydroShare(auth=auth)
            # resources = []
            # for r in hs.resources():
            #     resources.append(r)
            # return resources
            return resource_meta_data
        except TokenExpiredError:
            HydroShareAPI.refresh_token(hsaccount)
            token = hsaccount.get_token()
            auth = HydroShareAPI(client_id=client_id, client_secret=client_secret, token=token)

            hs = HydroShare(auth=auth)
            for resource in hs.resources():
                print(resource)
        except:
            return HttpResponseNotFound('resource not found for account ' + hsaccount.id)



class HydroShareAuth():
    def __init__(self, auth, account_info=None):
        self.access_token = auth['access_token']
        self.refresh_token = auth['refresh_token']
        self.expires_in = auth['expires_in']
        self.scope = auth['scope']
        if account_info:
            self.user_info = HydroShareUserInfo(account_info)


class HydroShareUserInfo():
    def __init__(self, info):
        self.id = info['id']
        self.email = info['email']
        self.first_name = info['first_name']
        self.last_name = info['last_name']
        self.organization = info['organization']
        self.username = info['username']

resource_meta_data = [
    {u'coverages': [], u'date_last_updated': u'11-21-2017', u'bag_url': u'http://www.hydroshare.org/django_irods/download/bags/f340e255d26246a0acd99097799d46c9.zip', u'science_metadata_url': u'http://www.hydroshare.org/hsapi/resource/f340e255d26246a0acd99097799d46c9/scimeta/', u'creator': u'Erica Loudermilk', u'resource_id': u'f340e255d26246a0acd99097799d46c9', u'resource_map_url': u'http://www.hydroshare.org/hsapi/resource/f340e255d26246a0acd99097799d46c9/map/', u'immutable': False, u'resource_title': u'Rapidan River Watershed near Ruckersville, VA', u'shareable': True, u'discoverable': True, u'published': False, u'date_created': u'11-21-2017', u'resource_url': u'http://www.hydroshare.org/resource/f340e255d26246a0acd99097799d46c9/', u'public': True, u'resource_type': u'CompositeResource'},
    {u'coverages': [], u'date_last_updated': u'11-21-2017', u'bag_url': u'http://www.hydroshare.org/django_irods/download/bags/f340e255d26246a0acd99097799d46c9.zip', u'science_metadata_url': u'http://www.hydroshare.org/hsapi/resource/f340e255d26246a0acd99097799d46c9/scimeta/', u'creator': u'Erica Loudermilk', u'resource_id': u'f340e255d26246a0acd99097799d46c9', u'resource_map_url': u'http://www.hydroshare.org/hsapi/resource/f340e255d26246a0acd99097799d46c9/map/', u'immutable': False, u'resource_title': u'Rapidan River Watershed near Ruckersville, VA', u'shareable': True, u'discoverable': True, u'published': False, u'date_created': u'11-21-2017', u'resource_url': u'http://www.hydroshare.org/resource/f340e255d26246a0acd99097799d46c9/', u'public': True, u'resource_type': u'CompositeResource'},
    {u'coverages': [], u'date_last_updated': u'11-21-2017', u'bag_url': u'http://www.hydroshare.org/django_irods/download/bags/261601bf5b654826be2fbf2f9574729f.zip', u'science_metadata_url': u'http://www.hydroshare.org/hsapi/resource/261601bf5b654826be2fbf2f9574729f/scimeta/', u'creator': u'Md Sabit', u'resource_id': u'261601bf5b654826be2fbf2f9574729f', u'resource_map_url': u'http://www.hydroshare.org/hsapi/resource/261601bf5b654826be2fbf2f9574729f/map/', u'immutable': False, u'resource_title': u'Estimating runoff at Ruckersville, VA using HEC-HMS, calibrating and validating the model', u'shareable': True, u'discoverable': True, u'published': False, u'date_created': u'11-21-2017', u'resource_url': u'http://www.hydroshare.org/resource/261601bf5b654826be2fbf2f9574729f/', u'public': True, u'resource_type': u'CompositeResource'},
    {u'coverages': [], u'date_last_updated': u'11-21-2017', u'bag_url': u'http://www.hydroshare.org/django_irods/download/bags/261601bf5b654826be2fbf2f9574729f.zip', u'science_metadata_url': u'http://www.hydroshare.org/hsapi/resource/261601bf5b654826be2fbf2f9574729f/scimeta/', u'creator': u'Md Sabit', u'resource_id': u'261601bf5b654826be2fbf2f9574729f', u'resource_map_url': u'http://www.hydroshare.org/hsapi/resource/261601bf5b654826be2fbf2f9574729f/map/', u'immutable': False, u'resource_title': u'Estimating runoff at Ruckersville, VA using HEC-HMS, calibrating and validating the model', u'shareable': True, u'discoverable': True, u'published': False, u'date_created': u'11-21-2017', u'resource_url': u'http://www.hydroshare.org/resource/261601bf5b654826be2fbf2f9574729f/', u'public': True, u'resource_type': u'CompositeResource'},
    {u'coverages': [{u'type': u'point', u'value': {u'units': u'Decimal degrees', u'east': -78.3403, u'north': 38.2806, u'name': u'Ruckersville, VA', u'projection': u'WGS 84 EPSG:4326'}}], u'date_last_updated': u'11-21-2017', u'bag_url': u'http://www.hydroshare.org/django_irods/download/bags/24128378656f467bad4ad5b32a79d56e.zip', u'science_metadata_url': u'http://www.hydroshare.org/hsapi/resource/24128378656f467bad4ad5b32a79d56e/scimeta/', u'creator': u'Faria Zahura', u'resource_id': u'24128378656f467bad4ad5b32a79d56e', u'resource_map_url': u'http://www.hydroshare.org/hsapi/resource/24128378656f467bad4ad5b32a79d56e/map/', u'immutable': False, u'resource_title': u'Hydrologic Model for Rapidian River near Ruckersville, VA', u'shareable': True, u'discoverable': True, u'published': False, u'date_created': u'11-21-2017', u'resource_url': u'http://www.hydroshare.org/resource/24128378656f467bad4ad5b32a79d56e/', u'public': True, u'resource_type': u'ModelInstanceResource'},
    {u'coverages': [{u'type': u'point', u'value': {u'units': u'Decimal degrees', u'east': -78.3403, u'north': 38.2806, u'name': u'Ruckersville, VA', u'projection': u'WGS 84 EPSG:4326'}}], u'date_last_updated': u'11-21-2017', u'bag_url': u'http://www.hydroshare.org/django_irods/download/bags/24128378656f467bad4ad5b32a79d56e.zip', u'science_metadata_url': u'http://www.hydroshare.org/hsapi/resource/24128378656f467bad4ad5b32a79d56e/scimeta/', u'creator': u'Faria Zahura', u'resource_id': u'24128378656f467bad4ad5b32a79d56e', u'resource_map_url': u'http://www.hydroshare.org/hsapi/resource/24128378656f467bad4ad5b32a79d56e/map/', u'immutable': False, u'resource_title': u'Hydrologic Model for Rapidian River near Ruckersville, VA', u'shareable': True, u'discoverable': True, u'published': False, u'date_created': u'11-21-2017', u'resource_url': u'http://www.hydroshare.org/resource/24128378656f467bad4ad5b32a79d56e/', u'public': True, u'resource_type': u'ModelInstanceResource'},
    {u'coverages': [{u'type': u'box', u'value': {u'northlimit': 30.1623230543248, u'projection': u'WGS 84 EPSG:4326', u'units': u'Decimal degrees', u'southlimit': 29.50025209413407, u'eastlimit': -97.44182761259479, u'westlimit': -98.71084148153477}}], u'date_last_updated': u'11-22-2017', u'bag_url': u'http://www.hydroshare.org/django_irods/download/bags/142ff904212144c2842abba738de8d14.zip', u'science_metadata_url': u'http://www.hydroshare.org/hsapi/resource/142ff904212144c2842abba738de8d14/scimeta/', u'creator': u'Dave Tarboton', u'resource_id': u'142ff904212144c2842abba738de8d14', u'resource_map_url': u'http://www.hydroshare.org/hsapi/resource/142ff904212144c2842abba738de8d14/map/', u'immutable': False, u'resource_title': u'SanMarcosFlowline', u'shareable': True, u'discoverable': True, u'published': False, u'date_created': u'11-22-2017', u'resource_url': u'http://www.hydroshare.org/resource/142ff904212144c2842abba738de8d14/', u'public': True, u'resource_type': u'GeographicFeatureResource'},
    {u'coverages': [{u'type': u'box', u'value': {u'northlimit': 30.1623230543248, u'projection': u'WGS 84 EPSG:4326', u'units': u'Decimal degrees', u'southlimit': 29.50025209413407, u'eastlimit': -97.44182761259479, u'westlimit': -98.71084148153477}}], u'date_last_updated': u'11-22-2017', u'bag_url': u'http://www.hydroshare.org/django_irods/download/bags/142ff904212144c2842abba738de8d14.zip', u'science_metadata_url': u'http://www.hydroshare.org/hsapi/resource/142ff904212144c2842abba738de8d14/scimeta/', u'creator': u'Dave Tarboton', u'resource_id': u'142ff904212144c2842abba738de8d14', u'resource_map_url': u'http://www.hydroshare.org/hsapi/resource/142ff904212144c2842abba738de8d14/map/', u'immutable': False, u'resource_title': u'SanMarcosFlowline', u'shareable': True, u'discoverable': True, u'published': False, u'date_created': u'11-22-2017', u'resource_url': u'http://www.hydroshare.org/resource/142ff904212144c2842abba738de8d14/', u'public': True, u'resource_type': u'GeographicFeatureResource'},
    {u'coverages': [], u'date_last_updated': u'11-22-2017', u'bag_url': u'http://www.hydroshare.org/django_irods/download/bags/571afcb0bbd14df995db3c472ca9dd3d.zip', u'science_metadata_url': u'http://www.hydroshare.org/hsapi/resource/571afcb0bbd14df995db3c472ca9dd3d/scimeta/', u'creator': u'Megan Fork', u'resource_id': u'571afcb0bbd14df995db3c472ca9dd3d', u'resource_map_url': u'http://www.hydroshare.org/hsapi/resource/571afcb0bbd14df995db3c472ca9dd3d/map/', u'immutable': False, u'resource_title': u'C budget and event-scale fluxes of DOC and TDN in urban engineered headwaters', u'shareable': True, u'discoverable': True, u'published': False, u'date_created': u'11-22-2017', u'resource_url': u'http://www.hydroshare.org/resource/571afcb0bbd14df995db3c472ca9dd3d/', u'public': False, u'resource_type': u'CompositeResource'},
    {u'coverages': [], u'date_last_updated': u'11-22-2017', u'bag_url': u'http://www.hydroshare.org/django_irods/download/bags/571afcb0bbd14df995db3c472ca9dd3d.zip', u'science_metadata_url': u'http://www.hydroshare.org/hsapi/resource/571afcb0bbd14df995db3c472ca9dd3d/scimeta/', u'creator': u'Megan Fork', u'resource_id': u'571afcb0bbd14df995db3c472ca9dd3d', u'resource_map_url': u'http://www.hydroshare.org/hsapi/resource/571afcb0bbd14df995db3c472ca9dd3d/map/', u'immutable': False, u'resource_title': u'C budget and event-scale fluxes of DOC and TDN in urban engineered headwaters', u'shareable': True, u'discoverable': True, u'published': False, u'date_created': u'11-22-2017', u'resource_url': u'http://www.hydroshare.org/resource/571afcb0bbd14df995db3c472ca9dd3d/', u'public': False, u'resource_type': u'CompositeResource'}
]

resource_ids = [
    'f340e255d26246a0acd99097799d46c9',
    'f340e255d26246a0acd99097799d46c9',
    '261601bf5b654826be2fbf2f9574729f',
    '261601bf5b654826be2fbf2f9574729f',
    '24128378656f467bad4ad5b32a79d56e',
    '24128378656f467bad4ad5b32a79d56e',
    '142ff904212144c2842abba738de8d14',
    '142ff904212144c2842abba738de8d14',
    '571afcb0bbd14df995db3c472ca9dd3d',
    '571afcb0bbd14df995db3c472ca9dd3d',
    # '73c8eabdc270480eadaf8ecd8d245a2c',
    # '73c8eabdc270480eadaf8ecd8d245a2c',
    # 'bd5e1952b73c42f8893c8a3f769de822',
    # 'bd5e1952b73c42f8893c8a3f769de822',
    # '3386b3136f514757b40a6cfbadfac91f',
    # '3386b3136f514757b40a6cfbadfac91f',
    # '8ec3822f5a284329804e81a4fbc6ff41',
    # '8ec3822f5a284329804e81a4fbc6ff41',
    # '58735a35f51f44b19dee8d3296abd067',
    # '58735a35f51f44b19dee8d3296abd067',
    # 'd1dd92c3bb6c498dab03bbdf93d13469',
    # 'd1dd92c3bb6c498dab03bbdf93d13469',
    # '9b30634e2c234253a2f82cdcedf0713d',
    # '9b30634e2c234253a2f82cdcedf0713d',
    # '1235c26fc4d04b2e987f7b3ed8515840',
    # '1235c26fc4d04b2e987f7b3ed8515840',
    # 'a003701d12a043879dcd107a381fa2ac',
    # 'a003701d12a043879dcd107a381fa2ac',
    # '1b9cc60d98984f9daac005d611437231',
    # '1b9cc60d98984f9daac005d611437231',
    # 'b3da3a5a0f354db4b446f22b799480b4',
    # 'b3da3a5a0f354db4b446f22b799480b4',
    # '6946805f095e46f495b6ab1c6dc064b5',
    # '6946805f095e46f495b6ab1c6dc064b5',
    # '9e860803f84940358a4dd0e563a96572',
    # '9e860803f84940358a4dd0e563a96572',
    # '96d5ca4012be43e282eb258f2ac1d525',
    # '96d5ca4012be43e282eb258f2ac1d525',
    # 'e85723aec277410fb1eddf91b12c304a',
    # 'e85723aec277410fb1eddf91b12c304a',
    # '47c92b3e1c3d42e9a9b871600be5b2bb',
    # '47c92b3e1c3d42e9a9b871600be5b2bb',
    # 'a9ed01021f5241128185f8267e9dce49',
    # 'a9ed01021f5241128185f8267e9dce49',
    # '6a53715771e4479a887eaa04614db4ea',
    # '6a53715771e4479a887eaa04614db4ea',
    # 'b56e4e9955cc4fef9ecfeef2aa736502',
    # 'b56e4e9955cc4fef9ecfeef2aa736502',
    # '5d5da76611d64b7a8105fadbc5ac7828',
    # '5d5da76611d64b7a8105fadbc5ac7828',
    # 'ddce4eb1a0cd48ffa0fdae4cdd33ad1f',
    # 'ddce4eb1a0cd48ffa0fdae4cdd33ad1f',
    # 'a2661d94a39e449bad34663c32cf485c',
    # 'a2661d94a39e449bad34663c32cf485c',
    # '0c9d72302aec43d3afc4d18637670947',
    # '0c9d72302aec43d3afc4d18637670947',
    # '0a613cda3ce34454ba6cacfc2c2d530d',
    # '0a613cda3ce34454ba6cacfc2c2d530d',
    # '33f6d7e5bd7d4e91a9bda0d59a754462',
    # '33f6d7e5bd7d4e91a9bda0d59a754462',
    # 'bf194be8851540c2af14010e1ae5331c',
    # 'bf194be8851540c2af14010e1ae5331c',
    # 'ae218c11c56b4f179bd16694cadcd013',
    # 'ae218c11c56b4f179bd16694cadcd013',
    # '439f02e76a5546e2bc8002bd31c3a1bb',
    # '439f02e76a5546e2bc8002bd31c3a1bb',
    # 'd341a600ae294d93b8a5662f5e2a2d8d',
    # 'd341a600ae294d93b8a5662f5e2a2d8d',
    # '4ce9bbaec61c473f87d0503a71a0d143',
    # '4ce9bbaec61c473f87d0503a71a0d143',
    # 'b35ca323d5f74e36ae90e9d968f96e51',
    # 'b35ca323d5f74e36ae90e9d968f96e51',
    # 'cb02607d82634cd788d9016ec3720749',
    # 'cb02607d82634cd788d9016ec3720749'
]