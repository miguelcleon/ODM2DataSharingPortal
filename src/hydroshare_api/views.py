from os import environ

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, Http404, HttpResponseServerError
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.utils.safestring import mark_safe
from dataloaderinterface.models import  ODM2User, HydroShareAccount
from hydroshare_util.Auth import HSUAuth
from .api import HydroShareAPI as hsAPI, HydroShareAPI

class HydroShareOAuthBaseClass(TemplateView):
    pass

class Resources(HydroShareOAuthBaseClass):
    template_name = 'hydroshare/resources.html'

    # noinspection PyArgumentList
    def get_context_data(self, **kwargs):
        context = super(Resources, self).get_context_data(**kwargs)
        if 'id' in kwargs:
            id = kwargs['id']
            try:
                account = HydroShareAccount.objects.get(id=id)
            except:
                raise Http404
            resources = HydroShareAPI.get_account_resources(account)
        else:
            resources = HydroShareAPI.get_shared_resources()

        # context['account'] = account
        context['resources'] = resources
        import json
        context['resources_json'] = json.dumps(resources)
        return context

    def get(self, request, *args, **kwargs):
        # HydroShareAPI.refresh_resources()
        return super(Resources, self).get(request, args, kwargs)


class OAuthAuthorize(HydroShareOAuthBaseClass):
    def get(self, request, *args, **kwargs):
        client_id = environ.get('HS_CLIENT_ID')
        client_secret = environ.get('HS_CLIENT_SECRET')
        redirect_uri = environ.get('HS_REDIRECT_URI')

        if 'code' in request.GET:
            auth = HSUAuth.authorize_client_callback(client_id, client_secret, redirect_uri, request.GET['code']) # type: HSUAuth

            if auth:
                user_info = auth.get_user_info()
                print("HydroShare user info: ", user_info)

                try:
                    user = HydroShareAccount.objects.get(ext_hydroshare_id=user_info['id'])
                except HydroShareAccount.DoesNotExist:
                    odm2user = ODM2User.objects.get(pk=request.user.id)
                    user = HydroShareAccount(user=odm2user, is_enabled=True, ext_hydroshare_id=user_info['id'])
                    user.save()

                token = auth.get_token()

                if token:
                    user.save_token(token)

                return redirect('user_account')
            else:
                # TODO: Create a view to handle failed authorization
                return HttpResponse('Error: Authorization failure!')
        elif 'error' in request.GET:
            return HttpResponseServerError(request.GET['error'])
        else:
            return HSUAuth.authorize_client(client_id, redirect_uri)


# TODO: Implement this class
class OAuthRefresh(HydroShareOAuthBaseClass):
#     def get(self, request, *args, **kwargs):
#         odmuser = ODM2User.objects.get(pk=request.user.id)
#         hsuser = HSUAccount.objects.get(user=odmuser)
#
#         params = hsAPI.get_refresh_code_params(hsuser.refresh_token)
#         r = requests.post(self.get_hydroshare_oauth_url('o/token/', params))
#
#         if r.status_code == 200:
#             odmuser = ODM2User.objects.get(pk=request.user.id)
#             user = HSUAccount.objects.get(user=odmuser)
#             user.set_token(r.json())
#
#             return redirect('user_account')
#         else:
#             # TODO: Create a view to handle failed authorization
#             return HttpResponse('Error: Authorization failure!')
    pass


class OAuthDeauthorize(HydroShareOAuthBaseClass):
    # TODO: Allow users to deauthorize this application
    pass

class OAuthAuthorizeRedirect(HydroShareOAuthBaseClass):
    template_name = 'hydroshare/oauth_redirect.html'

    # noinspection PyArgumentList
    def get_context_data(self, **kwargs):
        context = super(OAuthAuthorizeRedirect, self).get_context_data(**kwargs)
        context['hydroshare_oauth_url'] = mark_safe(HydroShareAPI.get_auth_code_url())
        return context



