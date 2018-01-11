import json
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.http import HttpResponse, Http404, HttpResponseServerError
from django.shortcuts import reverse
from django.views.generic import TemplateView
from django.utils.safestring import mark_safe
from hs_restclient import HydroShareNotFound

from hydroshare_api.api import *
from hydroshare_util.adapter import HydroShareAdapter
from dataloaderinterface.models import HydroShareAccount
from hydroshare_util.auth import AuthUtil
from hydroshare_util.utility import HydroShareUtility
import logging

class HydroShareOAuthBaseClass(TemplateView):
    pass

class ResourceBaseClass(TemplateView):
    """base class for resource views"""
    def get_hydroshare_util(self):
        try:
            accounts = HydroShareAccount.objects.filter(user=self.request.user.id)
        except HydroShareAccount.DoesNotExist:
            return HydroShareUtility()

        lenaccounts = len(accounts)
        if lenaccounts > 0:
            account = accounts[0]

            token = account.token.to_dict()
            auth = AuthUtil.authorize(token=token)

            return HydroShareUtility(auth=auth)
        else:
            return HydroShareUtility()


class Resources(ResourceBaseClass):
    """displays a list of shareable resources from hydroshare"""
    template_name = 'hydroshare/resources.html'

    def get_context_data(self, **kwargs):
        context = super(Resources, self).get_context_data(**kwargs)

        util = self.get_hydroshare_util()

        resources = util.get_resources()

        context['resources'] = resources
        context['resources_json'] = json.dumps(resources)
        return context

    def get(self, request, *args, **kwargs):
        # resources = util.get_resources()

        return super(Resources, self).get(request, args, kwargs)


class ResourceDetail(ResourceBaseClass):
    """displays the details for a specific hydroshare resource"""
    template_name = 'hydroshare/resources.html'

    def get_context_data(self, **kwargs):
        context = super(ResourceDetail, self).get_context_data(**kwargs)
        if 'id' in kwargs:
            id = kwargs['id']

            util = self.get_hydroshare_util()

            try:
                resource = util.get_resource_metadata(id)
                # resource = util.get_resource_metadata('f340e255d26246a0acd99097799d46c9')
                context['resource'] = resource
            except HydroShareNotFound:
                return Http404

        return context


class OAuthAuthorize(HydroShareOAuthBaseClass):
    """handles the OAuth 2.0 authorization workflow with hydroshare.org"""
    def get(self, request, *args, **kwargs):
        if 'code' in request.GET:
            try:
                token = AuthUtil.authorize_client_callback(request.GET['code'])  # type: dict
                auth_utility = AuthUtil.authorize(token=token)  # type: AuthUtil
            except Exception as e:
                print 'Authorizition likely failed: {}'.format(e)
                return HttpResponse('Error: Authorization failure!')

            client = auth_utility.get_client()  # type: HydroShareAdapter
            user_info = client.get_user_info()
            logging.info('\nuser_info: %s', json.dumps(user_info, indent=3))

            try:
                account = HydroShareAccount.objects.get(ext_hydroshare_id=user_info['id'])
            except ObjectDoesNotExist:
                account = HydroShareAccount(user=self.request.user.odm2user, is_enabled=True,
                                            ext_hydroshare_id=user_info['id'])
                account.save()

            account.save_token(token)

            return redirect('user_account')
        elif 'error' in request.GET:
            return HttpResponseServerError(request.GET['error'])
        else:
            return AuthUtil.authorize_client()


class OAuthAuthorizeRedirect(HydroShareOAuthBaseClass):
    """handles notifying a user they are being redirected, then handles the actual redirection"""
    template_name = 'hydroshare/oauth_redirect.html'

    def get_context_data(self, **kwargs):
        context = super(OAuthAuthorizeRedirect, self).get_context_data(**kwargs)
        url = reverse('hydroshare_api:oauth_redirect') + '?redirect=true'
        context['redirect_url'] = mark_safe(url)
        return context

    def get(self, request, *args, **kwargs):
        if 'redirect' in request.GET and request.GET['redirect'] == 'true':
            return AuthUtil.authorize_client()
        else:
            return super(OAuthAuthorizeRedirect, self).get(request, args, kwargs)


class OAuthRefresh(HydroShareOAuthBaseClass):
    # TODO: Implement this class
    pass


class OAuthDeauthorize(HydroShareOAuthBaseClass):
    # TODO: Implement this class
    pass
