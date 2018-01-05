from os import environ
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.utils.safestring import mark_safe
from dataloaderinterface.models import  ODM2User, HydroShareAccount
from hydroshare_util.Auth import HSUAuth
from .api import HydroShareAPI as hsAPI, HydroShareAPI


class HydroShareOAuthBaseClass(TemplateView):
    pass

class Resources(TemplateView):
    template_name = 'hydroshare/resources.html'

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
        return super(Resources, self).get(request, *args, **kwargs)


class OAuthAuthorize(HydroShareOAuthBaseClass):
    def get(self, request, *args, **kwargs):
        if 'code' in request.GET:

            # Get access token
            # auth = hsAPI.get_access_token(request.GET['code'])
            client_id = environ.get('HS_CLIENT_ID')
            client_secret = environ.get('HS_CLIENT_SECRET')
            redirect_uri = environ.get('HS_REDIRECT_URI')

            auth = HSUAuth.authorize_client_callback(client_id, client_secret, redirect_uri, request.GET['code']) # type: HSUAuth

            if auth:
                odm2user = ODM2User.objects.get(pk=request.user.id)
                try:
                    user = HydroShareAccount.objects.get(ext_hydroshare_id=auth.user_info.id)
                    # user_info = hsAPI.get_user_info(user.access_token)
                    # print(user_info)
                except HydroShareAccount.DoesNotExist:
                    user = HydroShareAccount(user=odm2user, is_enabled=True, ext_hydroshare_id=auth.user_info.id)
                    user.save()

                user.save_token(auth)

                return redirect('user_account')
            else:
                # TODO: Create a view to handle failed authorization
                return HttpResponse('Error: Authorization failure!')
        else:
            client_id = environ.get('HS_CLIENT_ID')
            client_secret = environ.get('HS_CLIENT_SECRET')
            redirect_uri = environ.get('HS_REDIRECT_URI')
            return HSUAuth.authorize_client(client_id, client_secret, redirect_uri)


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


# TODO: Allow users to deauthorize app to manage their HydroShare account.
class OAuthDeauthorize(HydroShareOAuthBaseClass):
    pass

class OAuthAuthorizeRedirect(HydroShareOAuthBaseClass):
    template_name = 'hydroshare/oauth_redirect.html'

    def get_context_data(self, **kwargs):
        context = super(OAuthAuthorizeRedirect, self).get_context_data(**kwargs)
        context['hydroshare_oauth_url'] = mark_safe(HydroShareAPI.get_auth_code_url())
        return context



