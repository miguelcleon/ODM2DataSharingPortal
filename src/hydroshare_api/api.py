import uuid
from os import environ as env
from datetime import date
import requests
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.http import HttpResponseServerError
from django.core.urlresolvers import reverse
from django.shortcuts import HttpResponseRedirect
from django.http import HttpResponseNotFound
from oauthlib.oauth2 import TokenExpiredError
from hs_restclient import HydroShare, HydroShareAuthOAuth2

from dataloaderinterface.models import HydroShareAccount
from hydroshare_api.models import HydroShareResource


class HydroShareAPI:

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
                return HydroShareAuth(resJSON, user_info)
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
        response = session.get("{url_base}{path}".format(url_base=HydroShareAPI._API_URL_BASE, path='userInfo/'),
                               headers=header)

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
        raise NotImplementedError

    @staticmethod
    def get_shared_resources():
        # TODO: Actually implement this method...
        mock_account = HydroShareAccount.objects.get(pk=1)
        return HydroShareAPI.get_account_resources(mock_account)

    @staticmethod
    def get_account_resources(hsaccount):
        client_id = HydroShareAPI.__client_id
        client_secret = HydroShareAPI.__client_secret
        token = hsaccount.token.to_dict()
        auth = HydroShareAuthOAuth2(client_id=client_id, client_secret=client_secret, token=token)

        try:
            # TODO: Return actual resources
            # hs = HydroShare(auth=auth)
            # resources = []
            # for r in hs.resources():
            #     resources.append(r)
            # return resources
            # return mock_resource_meta_data

            # mock_resources = []
            # for i in range(0, 10):
            #     resource_id = mock_resource_ids[i]
            #     mock_resources.append(hs.getSystemMetadata(resource_id))
            # print(mock_resources)
            # return mock_resources
            return mock_resource_meta_data
        except TokenExpiredError:
            HydroShareAPI.refresh_token(hsaccount)
            token = hsaccount.get_token()
            auth = HydroShareAPI(client_id=client_id, client_secret=client_secret, token=token)

            hs = HydroShare(auth=auth)
            for resource in hs.resources():
                print(resource)
        except:
            return HttpResponseNotFound('resource not found for account ' + hsaccount.id)

    @staticmethod
    def refresh_resources():
        # hs = HydroShare()
        # for resource in hs.resources():
        #     print(resource)
        HydroShareAPI._dev_refresh_resources()

    @staticmethod
    def _dev_refresh_resources():
        import csv
        with open('../resources.csv', 'rb') as file:
            reader = csv.DictReader(file)
            next(reader, None)
            for row in reader:
                try:
                    id = HydroShareAPI._string_to_uuid(row['resource_id'])
                    resource = HydroShareResource.objects.get(pk=id)
                    print('resource "' + str(resource.resource_id) + '" already exists.')
                except ObjectDoesNotExist:
                    print('Creating new resource.')
                    resource_obj = {
                        'resource_id': HydroShareAPI._string_to_uuid(row['resource_id']),
                        'resource_title': row['resource_title'],
                        'creator': row['creator'],
                        'resource_type': row['resource_type'],
                        'date_created': HydroShareAPI._hs_string_to_date(row['date_created']),
                        'date_last_updated': HydroShareAPI._hs_string_to_date(row['date_last_updated']),
                        'public': True if row['public'] == 'True' else False,
                        'shareable': True if row['shareable'] == 'True' else False,
                        'discoverable': True if row['discoverable'] == 'True' else False,
                        'published': True if row['published'] == 'True' else False,
                        'immutable': True if row['immutable'] == 'True' else False,
                        'resource_url': row['resource_url'],
                        'bag_url': row['bag_url'],
                        'science_metadata_url': row['science_metadata_url'],
                        'resource_map_url': row['resource_map_url']
                    }
                    resource = HydroShareResource(**resource_obj)
                    resource.save()

    @staticmethod
    def _string_to_uuid(s):
        return uuid.UUID(uuid.UUID(s).hex)

    @staticmethod
    def _hs_string_to_date(s):
        s = s.split('-')
        return "{year}-{month}-{day}".format(year=s[2], month=s[0], day=s[1])


class HydroShareAuth:
    token_type = 'Bearer'

    def __init__(self, auth, account_info=None):
        self.access_token = auth['access_token']
        self.refresh_token = auth['refresh_token']
        self.expires_in = auth['expires_in']
        self.scope = auth['scope']
        if account_info:
            self.user_info = HydroShareUserInfo(account_info)


class HydroShareUserInfo:
    def __init__(self, info):
        self.id = info['id']
        self.email = info['email']
        self.first_name = info['first_name']
        self.last_name = info['last_name']
        self.organization = info['organization']
        self.username = info['username']

mock_resource_meta_data =[
    {'coverages': [], 'date_last_updated': '11-21-2017', 'bag_url': 'http://www.hydroshare.org/django_irods/download/bags/f340e255d26246a0acd99097799d46c9.zip', 'science_metadata_url': 'http://www.hydroshare.org/hsapi/resource/f340e255d26246a0acd99097799d46c9/scimeta/', 'creator': 'Erica Loudermilk', 'resource_id': 'f340e255d26246a0acd99097799d46c9', 'resource_map_url': 'http://www.hydroshare.org/hsapi/resource/f340e255d26246a0acd99097799d46c9/map/', 'immutable': False, 'resource_title': 'Rapidan River Watershed near Ruckersville, VA', 'shareable': True, 'discoverable': True, 'published': False, 'date_created': '11-21-2017', 'resource_url': 'http://www.hydroshare.org/resource/f340e255d26246a0acd99097799d46c9/', 'public': True, 'resource_type': 'CompositeResource'},
    {'coverages': [], 'date_last_updated': '11-21-2017', 'bag_url': 'http://www.hydroshare.org/django_irods/download/bags/261601bf5b654826be2fbf2f9574729f.zip', 'science_metadata_url': 'http://www.hydroshare.org/hsapi/resource/261601bf5b654826be2fbf2f9574729f/scimeta/', 'creator': 'Md Sabit', 'resource_id': '261601bf5b654826be2fbf2f9574729f', 'resource_map_url': 'http://www.hydroshare.org/hsapi/resource/261601bf5b654826be2fbf2f9574729f/map/', 'immutable': False, 'resource_title': 'Estimating runoff at Ruckersville, VA using HEC-HMS, calibrating and validating the model', 'shareable': True, 'discoverable': True, 'published': False, 'date_created': '11-21-2017', 'resource_url': 'http://www.hydroshare.org/resource/261601bf5b654826be2fbf2f9574729f/', 'public': True, 'resource_type': 'CompositeResource'},
    {'coverages': [{'type': 'point', 'value': {'units': 'Decimal degrees', 'east': -78.3403, 'north': 38.2806, 'name': 'Ruckersville, VA', 'projection': 'WGS 84 EPSG:4326'}}], 'date_last_updated': '11-21-2017', 'bag_url': 'http://www.hydroshare.org/django_irods/download/bags/24128378656f467bad4ad5b32a79d56e.zip', 'science_metadata_url': 'http://www.hydroshare.org/hsapi/resource/24128378656f467bad4ad5b32a79d56e/scimeta/', 'creator': 'Faria Zahura', 'resource_id': '24128378656f467bad4ad5b32a79d56e', 'resource_map_url': 'http://www.hydroshare.org/hsapi/resource/24128378656f467bad4ad5b32a79d56e/map/', 'immutable': False, 'resource_title': 'Hydrologic Model for Rapidian River near Ruckersville, VA', 'shareable': True, 'discoverable': True, 'published': False, 'date_created': '11-21-2017', 'resource_url': 'http://www.hydroshare.org/resource/24128378656f467bad4ad5b32a79d56e/', 'public': True, 'resource_type': 'ModelInstanceResource'},
    {'coverages': [{'type': 'box', 'value': {'northlimit': 30.1623230543248, 'projection': 'WGS 84 EPSG:4326', 'units': 'Decimal degrees', 'southlimit': 29.50025209413407, 'eastlimit': -97.44182761259479, 'westlimit': -98.71084148153477}}], 'date_last_updated': '11-22-2017', 'bag_url': 'http://www.hydroshare.org/django_irods/download/bags/142ff904212144c2842abba738de8d14.zip', 'science_metadata_url': 'http://www.hydroshare.org/hsapi/resource/142ff904212144c2842abba738de8d14/scimeta/', 'creator': 'Dave Tarboton', 'resource_id': '142ff904212144c2842abba738de8d14', 'resource_map_url': 'http://www.hydroshare.org/hsapi/resource/142ff904212144c2842abba738de8d14/map/', 'immutable': False, 'resource_title': 'SanMarcosFlowline', 'shareable': True, 'discoverable': True, 'published': False, 'date_created': '11-22-2017', 'resource_url': 'http://www.hydroshare.org/resource/142ff904212144c2842abba738de8d14/', 'public': True, 'resource_type': 'GeographicFeatureResource'},
    {'coverages': [], 'date_last_updated': '11-22-2017', 'bag_url': 'http://www.hydroshare.org/django_irods/download/bags/571afcb0bbd14df995db3c472ca9dd3d.zip', 'science_metadata_url': 'http://www.hydroshare.org/hsapi/resource/571afcb0bbd14df995db3c472ca9dd3d/scimeta/', 'creator': 'Megan Fork', 'resource_id': '571afcb0bbd14df995db3c472ca9dd3d', 'resource_map_url': 'http://www.hydroshare.org/hsapi/resource/571afcb0bbd14df995db3c472ca9dd3d/map/', 'immutable': False, 'resource_title': 'C budget and event-scale fluxes of DOC and TDN in urban engineered headwaters', 'shareable': True, 'discoverable': True, 'published': False, 'date_created': '11-22-2017', 'resource_url': 'http://www.hydroshare.org/resource/571afcb0bbd14df995db3c472ca9dd3d/', 'public': False, 'resource_type': 'CompositeResource'},
    {'coverages': [], 'date_last_updated': '11-22-2017', 'bag_url': 'http://www.hydroshare.org/django_irods/download/bags/73c8eabdc270480eadaf8ecd8d245a2c.zip', 'science_metadata_url': 'http://www.hydroshare.org/hsapi/resource/73c8eabdc270480eadaf8ecd8d245a2c/scimeta/', 'creator': 'Christina Bandaragoda', 'resource_id': '73c8eabdc270480eadaf8ecd8d245a2c', 'resource_map_url': 'http://www.hydroshare.org/hsapi/resource/73c8eabdc270480eadaf8ecd8d245a2c/map/', 'immutable': False, 'resource_title': 'Infrastructure for Lowering the Barrier to Computational Modeling of the Earth Surface', 'shareable': True, 'discoverable': True, 'published': False, 'date_created': '11-22-2017', 'resource_url': 'http://www.hydroshare.org/resource/73c8eabdc270480eadaf8ecd8d245a2c/', 'public': True, 'resource_type': 'GenericResource'},
    {'coverages': [], 'date_last_updated': '11-29-2017', 'bag_url': 'http://www.hydroshare.org/django_irods/download/bags/bd5e1952b73c42f8893c8a3f769de822.zip', 'science_metadata_url': 'http://www.hydroshare.org/hsapi/resource/bd5e1952b73c42f8893c8a3f769de822/scimeta/', 'creator': 'Tyler Munk', 'resource_id': 'bd5e1952b73c42f8893c8a3f769de822', 'resource_map_url': 'http://www.hydroshare.org/hsapi/resource/bd5e1952b73c42f8893c8a3f769de822/map/', 'immutable': False, 'resource_title': 'Logan Canyon Runoff Factors', 'shareable': True, 'discoverable': True, 'published': False, 'date_created': '11-27-2017', 'resource_url': 'http://www.hydroshare.org/resource/bd5e1952b73c42f8893c8a3f769de822/', 'public': True, 'resource_type': 'CompositeResource'},
    {'coverages': [], 'date_last_updated': '11-28-2017', 'bag_url': 'http://www.hydroshare.org/django_irods/download/bags/3386b3136f514757b40a6cfbadfac91f.zip', 'science_metadata_url': 'http://www.hydroshare.org/hsapi/resource/3386b3136f514757b40a6cfbadfac91f/scimeta/', 'creator': 'Mary Lawrence', 'resource_id': '3386b3136f514757b40a6cfbadfac91f', 'resource_map_url': 'http://www.hydroshare.org/hsapi/resource/3386b3136f514757b40a6cfbadfac91f/map/', 'immutable': False, 'resource_title': 'Rapidan River', 'shareable': True, 'discoverable': True, 'published': False, 'date_created': '11-28-2017', 'resource_url': 'http://www.hydroshare.org/resource/3386b3136f514757b40a6cfbadfac91f/', 'public': True, 'resource_type': 'ModelInstanceResource'},
    {'coverages': [], 'date_last_updated': '11-28-2017', 'bag_url': 'http://www.hydroshare.org/django_irods/download/bags/8ec3822f5a284329804e81a4fbc6ff41.zip', 'science_metadata_url': 'http://www.hydroshare.org/hsapi/resource/8ec3822f5a284329804e81a4fbc6ff41/scimeta/', 'creator': 'Jennifer McIntosh', 'resource_id': '8ec3822f5a284329804e81a4fbc6ff41', 'resource_map_url': 'http://www.hydroshare.org/hsapi/resource/8ec3822f5a284329804e81a4fbc6ff41/map/', 'immutable': False, 'resource_title': 'Groundwater and gas chemistry and isotope data from coal beds in the Powder River Basin, Wyoming and Montana', 'shareable': True, 'discoverable': True, 'published': False, 'date_created': '11-28-2017', 'resource_url': 'http://www.hydroshare.org/resource/8ec3822f5a284329804e81a4fbc6ff41/', 'public': True, 'resource_type': 'GenericResource'},
    {'coverages': [], 'date_last_updated': '11-29-2017', 'bag_url': 'http://www.hydroshare.org/django_irods/download/bags/58735a35f51f44b19dee8d3296abd067.zip', 'science_metadata_url': 'http://www.hydroshare.org/hsapi/resource/58735a35f51f44b19dee8d3296abd067/scimeta/', 'creator': 'Tyler Munk', 'resource_id': '58735a35f51f44b19dee8d3296abd067', 'resource_map_url': 'http://www.hydroshare.org/hsapi/resource/58735a35f51f44b19dee8d3296abd067/map/', 'immutable': False, 'resource_title': 'Logan Canyon Presentation', 'shareable': True, 'discoverable': True, 'published': False, 'date_created': '11-29-2017', 'resource_url': 'http://www.hydroshare.org/resource/58735a35f51f44b19dee8d3296abd067/', 'public': True, 'resource_type': 'CompositeResource'}]

mock_resource_ids = [
    'f340e255d26246a0acd99097799d46c9',
    '261601bf5b654826be2fbf2f9574729f',
    '24128378656f467bad4ad5b32a79d56e',
    '142ff904212144c2842abba738de8d14',
    '571afcb0bbd14df995db3c472ca9dd3d',
    '73c8eabdc270480eadaf8ecd8d245a2c',
    'bd5e1952b73c42f8893c8a3f769de822',
    '3386b3136f514757b40a6cfbadfac91f',
    '8ec3822f5a284329804e81a4fbc6ff41',
    '58735a35f51f44b19dee8d3296abd067',
    'd1dd92c3bb6c498dab03bbdf93d13469',
    '9b30634e2c234253a2f82cdcedf0713d',
    '1235c26fc4d04b2e987f7b3ed8515840',
    'a003701d12a043879dcd107a381fa2ac',
    '1b9cc60d98984f9daac005d611437231',
    'b3da3a5a0f354db4b446f22b799480b4',
    '6946805f095e46f495b6ab1c6dc064b5',
    '9e860803f84940358a4dd0e563a96572',
    '96d5ca4012be43e282eb258f2ac1d525',
    'e85723aec277410fb1eddf91b12c304a',
    '47c92b3e1c3d42e9a9b871600be5b2bb',
    'a9ed01021f5241128185f8267e9dce49',
    '6a53715771e4479a887eaa04614db4ea',
    'b56e4e9955cc4fef9ecfeef2aa736502',
    '5d5da76611d64b7a8105fadbc5ac7828',
    'ddce4eb1a0cd48ffa0fdae4cdd33ad1f',
    'a2661d94a39e449bad34663c32cf485c',
    '0c9d72302aec43d3afc4d18637670947',
    '0a613cda3ce34454ba6cacfc2c2d530d',
    '33f6d7e5bd7d4e91a9bda0d59a754462',
    'bf194be8851540c2af14010e1ae5331c',
    'ae218c11c56b4f179bd16694cadcd013',
    '439f02e76a5546e2bc8002bd31c3a1bb',
    'd341a600ae294d93b8a5662f5e2a2d8d',
    '4ce9bbaec61c473f87d0503a71a0d143',
    'b35ca323d5f74e36ae90e9d968f96e51',
    'cb02607d82634cd788d9016ec3720749'
]