from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView
from os import environ as env
import requests
from dataloaderinterface.models import  ODM2User, HydroshareUser

BASE_HS_URL = 'https://www.hydroshare.org/'

class OAuthAuthorize(TemplateView):
    def get(self, request, **kwargs):

        if 'code' in request.GET:
            params = {
                'grant_type': 'authorization_code',
                'code': request.GET['code'],
                'client_id': env.get('HS_CLIENT_ID'),
                'client_secret': env.get('HS_CLIENT_SECRET'),
                'redirect_uri': env.get('HS_REDIRECT_URI')
            }

            url = get_url('o/token', params)
            r = requests.post(url)

            if r.status_code == 200:
                odmuser = ODM2User.objects.get(pk=request.user.id)
                user = HydroshareUser.objects.get(user=odmuser)
                user.set_token(r.json())

                return redirect('user_account')
            else:
                # TODO: Create a view to handle failed authorization
                return HttpResponse('Error: Authorization failure!')
        else:
            params = {
                'response_type': env.get('HS_RESPONSE_TYPE'),
                'client_id': env.get('HS_CLIENT_ID'),
                'redirect_uri': env.get('HS_REDIRECT_URI')
            }
            return redirect(get_url('o/authorize/', params))


class OAuthRefresh(TemplateView):
    def get(self, request, **kwargs):
        odmuser = ODM2User.objects.get(pk=request.user.id)
        hsuser = HydroshareUser.objects.get(user=odmuser)

        params = {
            'grant_type': 'refresh_token',
            'client_id': env.get('HS_CLIENT_ID'),
            'client_secret': env.get('HS_CLIENT_SECRET'),
            'refresh_token': hsuser.refresh_token,
            'redirect_uri': env.get('HS_REDIRECT_URI')
        }

        r = requests.post(get_url('o/token/', params))

        if r.status_code == 200:
            odmuser = ODM2User.objects.get(pk=request.user.id)
            user = HydroshareUser.objects.get(user=odmuser)
            user.set_token(r.json())

            return redirect('user_account')
        else:
            # TODO: Create a view to handle failed authorization
            return HttpResponse('Error: Authorization failure!')

class OAuthDeauthorize(TemplateView):
    # TODO: Allow users to deauthorize app to manage their HydroShare account.
    pass

def get_url(path, params):
    url_params = []
    for key, value in params.iteritems():
        url_params.append('{}={}'.format(key, value))
    return BASE_HS_URL + path + '?' + '&'.join(url_params)




