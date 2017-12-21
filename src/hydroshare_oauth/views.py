from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.utils.safestring import mark_safe
from dataloaderinterface.models import  ODM2User, HydroShareAccount
from .api import HydroShareAPI as hsAPI, HydroShareAPI


class HydroShareOAuthBaseClass(TemplateView):
    pass


class OAuthAuthorize(HydroShareOAuthBaseClass):
    def get(self, request, *args, **kwargs):
        if 'code' in request.GET:

            # Get access token
            auth = hsAPI.get_access_token(request.GET['code'])

            if auth:
                odm2user = ODM2User.objects.get(pk=request.user.id)
                try:
                    user = HydroShareAccount.objects.get(ext_hydroshare_id=auth.user_info.id)
                    # user_info = hsAPI.get_user_info(user.access_token)
                    # print(user_info)
                except HydroShareAccount.DoesNotExist:
                    user = HydroShareAccount(user=odm2user, is_enabled=True, ext_hydroshare_id=auth.user_info.id)
                    user.save()

                user.set_token(auth)

                return redirect('user_account')
            else:
                # TODO: Create a view to handle failed authorization
                return HttpResponse('Error: Authorization failure!')
        else:
            return hsAPI.authorize_client()


# TODO: Implement this class
class OAuthRefresh(HydroShareOAuthBaseClass):
#     def get(self, request, *args, **kwargs):
#         odmuser = ODM2User.objects.get(pk=request.user.id)
#         hsuser = HydroShareAccount.objects.get(user=odmuser)
#
#         params = hsAPI.get_refresh_code_params(hsuser.refresh_token)
#         r = requests.post(self.get_hydroshare_oauth_url('o/token/', params))
#
#         if r.status_code == 200:
#             odmuser = ODM2User.objects.get(pk=request.user.id)
#             user = HydroShareAccount.objects.get(user=odmuser)
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



