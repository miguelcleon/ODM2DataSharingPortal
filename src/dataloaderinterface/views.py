# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from uuid import uuid4
import json
import requests
import re
import logging

from django.conf import settings
from django.db.models.aggregates import Max
from django.db.models.expressions import F
from django.db.models.query import Prefetch
from django.utils.safestring import mark_safe

from dataloaderservices.views import CSVDataApi

from dataloader.models import FeatureAction, Result, ProcessingLevel, TimeSeriesResult, SamplingFeature, \
    SpatialReference, \
    ElevationDatum, SiteType, ActionBy, Action, Method, DataLoggerProgramFile, DataLoggerFile, \
    InstrumentOutputVariable, DataLoggerFileColumn, TimeSeriesResultValue
from leafpack.models import LeafPack, LeafPackBug, Macroinvertebrate
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponseRedirect, Http404, HttpResponse, JsonResponse, HttpResponseServerError
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView, FormView, ModelFormMixin
from django.views.generic.list import ListView
from django.core.management import call_command

from dataloaderinterface.forms import SamplingFeatureForm, ResultFormSet, SiteForm, \
    OrganizationForm, ActionByForm, HydroShareSettingsForm, SiteAlertForm, \
    HydroShareResourceDeleteForm, SiteRegistrationForm, SiteSensorForm
from dataloaderinterface.models import ODM2User, SiteRegistration, SiteSensor, HydroShareAccount, HydroShareResource, \
    SiteAlert, OAuthToken
from hydroshare_util import HydroShareNotFound, HydroShareHTTPException
from hydroshare_util.utility import HydroShareUtility
from hydroshare_util.adapter import HydroShareAdapter
from hydroshare_util.auth import AuthUtil
from hydroshare_util.resource import Resource
from hydroshare_util.coverage import PointCoverage, BoxCoverage, PeriodCoverage, Coverage
from accounts.models import User


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls):
        return login_required(super(LoginRequiredMixin, cls).as_view())


class HomeView(TemplateView):
    template_name = 'dataloaderinterface/home.html'


class SitesListView(LoginRequiredMixin, ListView):
    model = SiteRegistration
    context_object_name = 'sites'
    template_name = 'dataloaderinterface/my-sites.html'

    def get_queryset(self):
        return super(SitesListView, self).get_queryset()\
            .with_sensors()\
            .with_latest_measurement_id()\
            .deployed_by(user_id=self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super(SitesListView, self).get_context_data()
        context['followed_sites'] = super(SitesListView, self).get_queryset()\
            .with_sensors() \
            .with_latest_measurement_id() \
            .followed_by(user_id=self.request.user.id)
        return context


class StatusListView(ListView):
    model = SiteRegistration
    context_object_name = 'sites'
    template_name = 'dataloaderinterface/status.html'

    def get_queryset(self):
        return super(StatusListView, self).get_queryset()\
            .with_status_sensors()\
            .deployed_by(self.request.user.id) \
            .with_latest_measurement_id() \
            .order_by('sampling_feature_code')

    def get_context_data(self, **kwargs):
        context = super(StatusListView, self).get_context_data(**kwargs)
        context['followed_sites'] = super(StatusListView, self).get_queryset()\
            .with_status_sensors()\
            .followed_by(user_id=self.request.user.id) \
            .with_latest_measurement_id() \
            .order_by('sampling_feature_code')
        return context


class BrowseSitesListView(ListView):
    model = SiteRegistration
    context_object_name = 'sites'
    template_name = 'dataloaderinterface/browse-sites.html'

    def get_queryset(self):
        return super(BrowseSitesListView, self).get_queryset()\
            .with_sensors()\
            .with_leafpacks()\
            .with_latest_measurement_id()\
            .with_ownership_status(self.request.user.id)


class SiteDetailView(DetailView):
    model = SiteRegistration
    context_object_name = 'site'
    slug_field = 'sampling_feature_code'
    slug_url_kwarg = 'sampling_feature_code'
    template_name = 'dataloaderinterface/site_details.html'

    def get_queryset(self):
        return super(SiteDetailView, self).get_queryset().with_sensors().with_sensors_last_measurement()

    def get_context_data(self, **kwargs):
        context = super(SiteDetailView, self).get_context_data(**kwargs)
        context['is_followed'] = self.object.followed_by.filter(id=self.request.user.id).exists()
        context['can_administer_site'] = self.request.user.can_administer_site(self.object)
        context['is_site_owner'] = self.request.user == self.object.django_user
        context['tsa_url'] = settings.TSA_URL

        context['leafpacks'] = LeafPack.objects.filter(site_registration=context['site'].pk)

        try:
            context["hydroshare_account"] = self.request.user.hydroshare_account
        except AttributeError:
            pass

        try:
            resources = HydroShareResource.objects.filter(site_registration=context['site'].pk)
            visible_resources = [res for res in resources if res.visible]
            context['resource_is_connected'] = len(visible_resources) > 0
        except ObjectDoesNotExist:
            pass

        return context


class HydroShareResourceViewMixin:
    def __init__(self):
        self.request = None

    def get_hs_resource(self, resource):  # type: (HydroShareResource) -> Resource
        """ Creates a 'hydroshare_util.Resource' object """
        account = self.request.user.hydroshare_account
        token_json = account.get_token()
        auth_util = AuthUtil.authorize(token=token_json)

        # if the oauth access_token expires in less than a week, refresh the token
        seconds_in_week = 60*60*24*7
        if token_json.get('expires_in', seconds_in_week) < seconds_in_week:
            try:
                auth_util.refresh_token()
                account.update_token(auth_util.get_token())
            except Exception as e:
                print(e)

        hs_resource = Resource(auth_util.get_client())
        hs_resource.resource_id = resource.ext_id
        return hs_resource


class HydroShareResourceBaseView(UpdateView):
    slug_field = 'sampling_feature_code'

    def form_invalid(self, form):
        response = super(HydroShareResourceBaseView, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def get_object(self, queryset=None, **kwargs):
        site = SiteRegistration.objects.get(sampling_feature_code=self.kwargs[self.slug_field])
        resource = None

        try:
            # Filter through resources that are visible; there should only be one, so pick the first
            resource = HydroShareResource.objects.filter(site_registration=site.registration_id, visible=True).first()
        except ObjectDoesNotExist:
            pass
        return resource

    def get_context_data(self, **kwargs):
        context = super(HydroShareResourceBaseView, self).get_context_data(**kwargs)
        context['date_format'] = settings.DATETIME_FORMAT
        return context

    def get(self, request, *args, **kwargs):
        # # uncomment to force a hydroshare resource file update.
        # # Only do this for debugging purposes!
        # call_command('update_hydroshare_resource_files', '--force-update')
        return super(HydroShareResourceBaseView, self).get(request, args, kwargs)


class HydroShareResourceCreateView(HydroShareResourceBaseView, HydroShareResourceViewMixin):
    template_name = 'hydroshare/hs_site_details.html'
    model = HydroShareResource
    object = None
    fields = '__all__'

    ABSTRACT_PROTO = u"The data contained in this resource were uploaded from the WikiWatershed Data Sharing Portal " \
        u"– http://data.wikiwatershed.org. They were collected at a site named {site_name}. The full URL to access " \
        u"this site in the WikiWatershed Data Sharing portal is: http://data.wikiwatershed.org/sites/{site_code}/."

    TITLE_PROTO = "Data from {site_name} uploaded from the WikiWatershed Data Sharing Portal"

    def generate_abstract(self, site):
        return self.ABSTRACT_PROTO.format(site_name=site.sampling_feature_name, site_code=site.sampling_feature_code)

    def generate_title(self, site):
        return self.TITLE_PROTO.format(site_name=site.sampling_feature_name)

    def get_context_data(self, **kwargs):
        context = super(HydroShareResourceCreateView, self).get_context_data(**kwargs)
        site = SiteRegistration.objects.get(sampling_feature_code=self.kwargs[self.slug_field])
        initial_datatype = HydroShareSettingsForm.data_type_choices[0][0]

        # Cycle through resources to make sure they still exist on hydroshare.org
        resources = HydroShareResource.objects.filter(site_registration=site.pk, visible=False)
        for resource in resources:
            hs_resource = self.get_hs_resource(resource)
            try:
                # Basically, just make request to see if the resource still exists. This request can be anything
                hs_resource.get_access_level()
            except HydroShareNotFound:
                resource.delete()

        context['site'] = site
        form = HydroShareSettingsForm(initial={'site_registration': site.pk,
                                               'data_types': [initial_datatype],
                                               'pause_sharing': False,
                                               'title': self.generate_title(site),
                                               'abstract': self.generate_abstract(site)})
        form.fields['resources'].queryset = HydroShareResource.objects.filter(site_registration=site.pk, visible=False)
        context['form'] = form
        return context

    def create_resource(self, site, form):
        hs_account = self.request.user.hydroshare_account

        resource = HydroShareResource(site_registration=site,
                                      hs_account=hs_account,
                                      data_types=",".join(form.cleaned_data['data_types']),
                                      update_freq=form.cleaned_data['update_freq'],
                                      sync_type=form.cleaned_data['schedule_type'],
                                      is_enabled=True,
                                      title=form.cleaned_data['title'],
                                      last_sync_date=timezone.now())

        token_json = hs_account.get_token()
        client = AuthUtil.authorize(token=token_json).get_client()
        hs_resource = Resource(client)

        hs_resource.owner = Resource.DEFAULT_OWNER
        hs_resource.resource_type = Resource.COMPOSITE_RESOURCE
        hs_resource.creator = '{0} {1}'.format(self.request.user.first_name, self.request.user.last_name)
        hs_resource.abstract = form.cleaned_data['abstract']
        hs_resource.title = form.cleaned_data['title']
        hs_resource.public = True

        coverage = PointCoverage(name=site.sampling_feature_name, latitude=site.latitude, longitude=site.longitude)
        hs_resource.add_coverage(coverage)

        # Add 'WikiWatershed' keyword to all resources
        hs_resource.keywords.add('WikiWatershed')

        sensors = SiteSensor.objects.filter(registration=site)
        if len(sensors):
            # If this site has sensors, add 'EnviroDIY' keyword.
            hs_resource.keywords.add('EnviroDIY')
            # Add sensor variable names as keywords
            for sensor in sensors:
                hs_resource.keywords.add(sensor.variable_name)

        # TODO: Clearly, this will need to change once Leaf Packet datasets are actually integrated into the project
        if getattr(resource, 'look_at_me_I_have_leaf_packet_datasets_yay', None):
            hs_resource.keywords.add('Leaf Pack')

        try:
            """
            NOTE: The UUID returned when creating a resource on hydroshare.org is externally generated and should only 
            be used as a reference to an external datasource that is not part of ODM2WebSDL database ecosystem.
            """
            resource.ext_id = hs_resource.create()
            resource.title = hs_resource.title
        except HydroShareHTTPException as e:
            return JsonResponse({"error": e.message,
                                 "message": "There was a problem with hydroshare.org and your resource was not created. You might want to see if www.hydroshare.org is working and try again later."},
                                status=e.status_code)

        resource.save()
        return hs_resource

    def post(self, request, *args, **kwargs):
        """
        Creates a resource in hydroshare.org using form data.
        """

        # NOTE: Eventually EnviroDIY will support multiple data types. For now, this defaults to 'TS' (Time Series)
        post_data = request.POST.copy()
        post_data.update({'data_types': 'TS'})
        form = HydroShareSettingsForm(post_data)

        if form.is_valid():
            site = SiteRegistration.objects.get(sampling_feature_code=self.kwargs[self.slug_field])

            if form.cleaned_data['resources']:
                resource = form.cleaned_data['resources']
                resource.visible = True
                resource.data_types = ",".join(form.cleaned_data['data_types'])
                resource.update_freq = form.cleaned_data['update_freq']
                resource.sync_type = form.cleaned_data['schedule_type']
                resource.is_enabled = True
                resource.last_sync_date = timezone.now()
                resource.title = form.cleaned_data['title']
                resource.save()
                hs_resource = self.get_hs_resource(resource)
                hs_resource.update({'title': form.cleaned_data['title'],
                                    'description': form.cleaned_data['abstract']})
            else:
                hs_resource = self.create_resource(site, form)

            # Upload data files to the newly created resource
            try:
                upload_hydroshare_resource_files(site, hs_resource)
            except Exception as e:
                # If the app fails here, the resource was created but the resource files failed to upload.
                logging.error('Failed to upload resource files: ' + e.message)

            success_url = reverse('site_detail', kwargs={'sampling_feature_code': site.sampling_feature_code})

            if self.request.is_ajax():
                return JsonResponse({'redirect': success_url})
            else:
                return redirect(success_url)
        else:
            return self.form_invalid(form)


class HydroShareResourceUpdateView(HydroShareResourceViewMixin, HydroShareResourceBaseView):
    template_name = 'hydroshare/hs_site_details.html'
    model = HydroShareResource
    slug_field = 'sampling_feature_code'
    slug_url_kwarg = 'hydroshare_settings_id'
    fields = '__all__'
    object = None

    def get_context_data(self, **kwargs):
        context = super(HydroShareResourceUpdateView, self).get_context_data(**kwargs)
        site = SiteRegistration.objects.get(sampling_feature_code=self.kwargs['sampling_feature_code'])
        resource = self.get_object()
        context['site'] = site
        context['resource'] = resource
        context['form'] = HydroShareSettingsForm(initial={
            'site_registration': site.pk,
            'update_freq': resource.update_freq,
            'schedule_type': resource.sync_type,
            'pause_sharing': not resource.is_enabled,
            'data_types': resource.data_types.split(",")
        })

        context['delete_form'] = HydroShareResourceDeleteForm()

        hs_resource = self.get_hs_resource(resource)
        try:
            metadata = hs_resource.get_system_metadata(timeout=10.0)
            context['resource_is_published'] = metadata.get("published", False)

            # Update the title in case the owner changed it
            if 'resource_title' in metadata:
                resource.title = metadata['resource_title']
                resource.save()

        except HydroShareNotFound:
            context['resource_not_found'] = True
        except requests.exceptions.Timeout:
            context['request_timeout'] = True
        finally:
            # if the resource was not found or the resource is published, provide the 'delete_resource_url'
            if context.get('resource_not_found', None) is True or context.get('resource_is_published', None):
                context['delete_resource_url'] = reverse('hs_resource_delete',
                                                         kwargs={'sampling_feature_code': site.sampling_feature_code})

        return context

    def post(self, request, *args, **kwargs):
        form = HydroShareSettingsForm(request.POST)

        if form.is_valid():
            site = SiteRegistration.objects.get(pk=form.cleaned_data['site_registration'])
            resource = self.get_object()

            if 'update_files' in request.POST and resource.is_enabled:
                # get hydroshare resource info using hydroshare_util; this will get authentication info needed to
                # upload files to the resource.
                hs_resource = self.get_hs_resource(resource)

                # Upload the most recent resource files
                try:
                    upload_hydroshare_resource_files(site, hs_resource)
                except Exception as e:
                    return JsonResponse({'error': e.message}, status=500)

                # update last sync date on resource
                resource.last_sync_date = timezone.now()
            else:
                resource.data_types = ",".join(form.cleaned_data['data_types'])
                resource.update_freq = form.cleaned_data['update_freq']
                resource.sync_type = form.cleaned_data['schedule_type']
                resource.is_enabled = not form.cleaned_data["pause_sharing"]

            resource.save()

            success_url = reverse('site_detail', kwargs={'sampling_feature_code': site.sampling_feature_code})
            if self.request.is_ajax():
                return JsonResponse({'redirect': success_url})
            else:
                return redirect(success_url)
        else:
            response = self.form_invalid(form)
            return response


class HydroShareResourceDeleteView(LoginRequiredMixin, HydroShareResourceViewMixin, DeleteView):
    model = HydroShareResource
    slug_field = 'sampling_feature_code'
    slug_url_kwarg = 'sampling_feature_code'

    def get_site_registration(self):
        try:
            code = self.kwargs.get('sampling_feature_code', '')
            site = SiteRegistration.objects.get(sampling_feature_code=code)
        except ObjectDoesNotExist:
            return None
        return site

    def get_object(self, queryset=None, **kwargs):
        site = kwargs['site']
        resource = None
        try:
            # Find the resource that is currently visible; there should only be one.
            resource = HydroShareResource.objects.filter(site_registration=site.registration_id, visible=True).first()
        except ObjectDoesNotExist:
            pass
        return resource

    def get(self, request, *arg, **kwargs):
        site = self.get_site_registration()
        return redirect(reverse('site_detail', kwargs={'sampling_feature_code': site.sampling_feature_code}))

    def post(self, request, *args, **kwargs):
        site = self.get_site_registration()
        resource = self.get_object(site=site)

        form = HydroShareResourceDeleteForm(request.POST)
        if form.is_valid():
            delete_external_resource = form.cleaned_data.get('delete_external_resource')

            if delete_external_resource is True:
                # delete resource in hydroshare.org if delete_external_resource is True
                hs_resource = self.get_hs_resource(resource)
                try:
                    hs_resource.delete()
                except Exception as error:
                    print(error)
                resource.delete()
            else:
                # Don't delete the resource, but instead turn visibility off. This is so the user can reconnect the
                # resource after disconnecting it.
                resource.visible = False
                resource.save()

        return redirect(reverse('site_detail', kwargs={'sampling_feature_code': site.sampling_feature_code}))


class SiteDeleteView(LoginRequiredMixin, DeleteView):
    model = SiteRegistration
    slug_field = 'sampling_feature_code'
    slug_url_kwarg = 'sampling_feature_code'
    success_url = reverse_lazy('sites_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.can_administer_site(self.get_object()):
            raise Http404
        return super(SiteDeleteView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return redirect(reverse('site_detail', kwargs={'sampling_feature_code': self.get_object().sampling_feature_code}))

    def post(self, request, *args, **kwargs):
        site_registration = self.get_object()
        site_registration.delete()

        messages.success(request, 'The site has been deleted successfully.')
        return HttpResponseRedirect(self.success_url)


class SiteUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'dataloaderinterface/site_registration_update.html'
    slug_url_kwarg = 'sampling_feature_code'
    slug_field = 'sampling_feature_code'
    form_class = SiteRegistrationForm
    model = SiteRegistration
    object = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.can_administer_site(self.get_object()):
            raise Http404

        return super(SiteUpdateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('site_detail', kwargs={'sampling_feature_code': self.object.sampling_feature_code})

    def get_queryset(self):
        return super(SiteUpdateView, self).get_queryset().with_sensors()

    def get_hydroshare_accounts(self):
        try:
            return HydroShareAccount.objects.filter(user=self.request.user.id)
        except ObjectDoesNotExist:
            return []

    def get_context_data(self, **kwargs):
        data = self.request.POST or {}
        context = super(SiteUpdateView, self).get_context_data()

        sampling_feature_code = self.get_object().sampling_feature_code

        site_alert = self.request.user.site_alerts\
            .filter(site_registration__sampling_feature_code=sampling_feature_code)\
            .first()

        alert_data = {'notify': True, 'hours_threshold': int(site_alert.hours_threshold.total_seconds() / 3600)} \
            if site_alert \
            else {}

        # maybe just access site.leafpacks in the template?
        context['leafpacks'] = LeafPack.objects.filter(site_registration=self.get_object())
        context['sensor_form'] = SiteSensorForm(initial={'registration': self.get_object().registration_id})
        context['email_alert_form'] = SiteAlertForm(data=alert_data)
        context['zoom_level'] = data['zoom-level'] if 'zoom-level' in data else None

        return context

    def post(self, request, *args, **kwargs):
        site_registration = self.get_object()
        form = self.get_form_class()(request.POST, instance=site_registration)
        notify_form = SiteAlertForm(request.POST)

        if form.is_valid() and notify_form.is_valid():
            form.instance.affiliation_id = form.cleaned_data['affiliation_id'] or request.user.affiliation_id

            site_alert = self.request.user.site_alerts.filter(site_registration=site_registration).first()

            if notify_form.cleaned_data['notify'] and site_alert:
                site_alert.hours_threshold = timedelta(hours=int(notify_form.data['hours_threshold']))
                site_alert.save()

            elif notify_form.cleaned_data['notify'] and not site_alert:
                self.request.user.site_alerts.create(
                    site_registration=site_registration,
                    hours_threshold=timedelta(hours=int(notify_form.data['hours_threshold']))
                )

            elif not notify_form.cleaned_data['notify'] and site_alert:
                site_alert.delete()

            messages.success(request, 'The site has been updated successfully.')
            return self.form_valid(form)
        else:
            messages.error(request, 'There are still some required fields that need to be filled out!')
            return self.form_invalid(form)


class SiteRegistrationView(LoginRequiredMixin, CreateView):
    template_name = 'dataloaderinterface/site_registration.html'
    form_class = SiteRegistrationForm
    model = SiteRegistration
    object = None

    def get_success_url(self):
        return reverse_lazy('site_detail', kwargs={'sampling_feature_code': self.object.sampling_feature_code})

    @staticmethod
    def get_default_data():
        data = {
            'elevation_datum': ElevationDatum.objects.filter(pk='MSL').first(),
            'site_type': SiteType.objects.filter(pk='Stream').first()
        }
        return data

    def get_form(self, form_class=None):
        return self.get_form_class()(initial=self.get_default_data())

    def get_context_data(self, **kwargs):
        context = super(SiteRegistrationView, self).get_context_data()
        data = self.request.POST or {}
        context['email_alert_form'] = SiteAlertForm(data)
        context['zoom_level'] = data['zoom-level'] if 'zoom-level' in data else None
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form_class()(request.POST)
        notify_form = SiteAlertForm(request.POST)

        if form.is_valid() and notify_form.is_valid():
            form.instance.affiliation_id = form.cleaned_data['affiliation_id'] or request.user.affiliation_id
            self.object = form.save()

            if notify_form.cleaned_data['notify']:
                self.request.user.site_alerts.create(
                    site_registration=form.instance,
                    hours_threshold=timedelta(hours=int(notify_form.data['hours_threshold']))
                )
            return super(ModelFormMixin, self).form_valid(form)
        else:
            messages.error(request, 'There are still some required fields that need to be filled out!')
            return self.form_invalid(form)


class OAuthAuthorize(TemplateView):
    """handles the OAuth 2.0 authorization workflow with hydroshare.org"""
    def get(self, request, *args, **kwargs):
        if 'code' in request.GET:
            try:
                token_dict = AuthUtil.authorize_client_callback(request)  # type: dict
                auth_util = AuthUtil.authorize(token=token_dict)  # type: AuthUtil
            except Exception as e:
                print 'Authorizition failure: {}'.format(e)
                return HttpResponse(mark_safe("<p>Error: Authorization failure!</p><p>{e}</p>".format(e=e)))

            client = auth_util.get_client()  # type: HydroShareAdapter
            user_info = client.getUserInfo()
            print('\nuser_info: %s', json.dumps(user_info, indent=3))

            try:
                # check if hydroshare account already exists
                account = HydroShareAccount.objects.get(ext_id=user_info['id'])
            except ObjectDoesNotExist:
                # if account does not exist, create a new one
                account = HydroShareAccount(is_enabled=True, ext_id=user_info['id'])

            old_token = None
            if account.token:
                old_token = account.token
                account.token = None
                account.save()

            # Make updates to datatbase
            token = OAuthToken(**token_dict)
            token.save()

            account.token = token
            account.save()

            if old_token:
                old_token.delete()

            user = request.user
            user.hydroshare_account = account
            user.save()
            # odm2user = ODM2User.objects.get(user=request.user.pk)
            # odm2user.hydroshare_account = account
            # odm2user.save()

            return redirect('user_account')
        elif 'error' in request.GET:
            return HttpResponseServerError(request.GET['error'])
        else:
            return AuthUtil.authorize_client(request)


class OAuthRedirect(TemplateView):
    """
    handles notifying a user they are being redirected, then handles the actual redirection

    When a user comes to this view, 'self.get()' checks for a 'redirect' value in the url parameters.

        - If the value is found, the user will be immediately redirected to www.hydroshare.org for client
        authorization.

        - If the value is NOT found, the user is sent to a page notifying them that they are about to be redirected.
        After a couple of seconds, they are redirected back to this view with the 'redirect' parameter contained in the
        url, and sent off to www.hydroshare.org.
    """
    template_name = 'hydroshare/oauth_redirect.html'

    def get_context_data(self, **kwargs):
        context = super(OAuthRedirect, self).get_context_data(**kwargs)

        # Get the current scheme (http or https)
        scheme = self.request.is_secure() and "https" or "http"
        # Need to get the host since the host name can be 'data.envirodiy.org' or 'data.wikiwatershed.org'
        host = self.request.META.get('HTTP_HOST', None)
        # Build the url and add 'redirect' into the url params
        url = '{scheme}://{host}{url}?{params}'.format(scheme=scheme, host=host,
                                                       url=reverse('hydroshare_oauth_redirect'), params='redirect=true')

        context['redirect_url'] = mark_safe(url)

        return context

    def get(self, request, *args, **kwargs):
        if 'redirect' in request.GET and request.GET['redirect'] == 'true':
            return AuthUtil.authorize_client(request)

        return super(OAuthRedirect, self).get(request, args, kwargs)


# def delete_result(result):
#     result_id = result.result_id
#     feature_action = result.feature_action
#     action = feature_action.action
#
#     result.data_logger_file_columns.all().delete()
#     result.timeseriesresult.values.all().delete()
#     result.timeseriesresult.delete()
#
#     action.action_by.all().delete()
#     result.delete()
#
#     feature_action.delete()
#     action.delete()
#     SiteSensor.objects.filter(result_id=result_id).delete()


def get_site_files(site_registration):
    site_sensors = SiteSensor.objects.filter(registration=site_registration.pk)
    files = []
    for site_sensor in site_sensors:
        filename, csv_file = CSVDataApi.get_csv_file(site_sensor.result_id)
        files.append((filename, csv_file.getvalue()))

    return files


def upload_hydroshare_resource_files(site, resource):  # type: (SiteRegistration, Resource) -> None
    files = get_site_files(site)
    for file_ in files:
        file_name = file_[0]
        content = file_[1]
        resource.upload_file(file_name, content)
