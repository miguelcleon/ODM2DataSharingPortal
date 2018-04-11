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
from django.contrib import messages
from django.contrib.auth import login
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
from django.views.generic.edit import UpdateView, CreateView, DeleteView, FormView
from django.views.generic.list import ListView
from django.core.management import call_command

from dataloaderinterface.forms import SamplingFeatureForm, ResultFormSet, SiteForm, UserRegistrationForm, \
    OrganizationForm, UserUpdateForm, ActionByForm, HydroShareSiteForm, HydroShareSettingsForm, SiteAlertForm, \
    HydroShareResourceDeleteForm, SampledMediumField
from dataloaderinterface.models import ODM2User, SiteRegistration, SiteSensor, HydroShareAccount, HydroShareResource, \
    SiteAlert, OAuthToken
from hydroshare_util import HydroShareNotFound, HydroShareHTTPException
from hydroshare_util.utility import HydroShareUtility
from hydroshare_util.adapter import HydroShareAdapter
from hydroshare_util.auth import AuthUtil
from hydroshare_util.resource import Resource
from hydroshare_util.coverage import PointCoverage, BoxCoverage, PeriodCoverage, Coverage


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls):
        return login_required(super(LoginRequiredMixin, cls).as_view())


class HomeView(TemplateView):
    template_name = 'dataloaderinterface/home.html'

    # def get_context_data(self, **kwargs):
    #     context = super(HomeView, self).get_context_data()
    #     context['device_results'] = []
    #     for device in DeviceRegistration.objects.get_queryset().filter(user=self.request.user.id):
    #         sampling_feature = SamplingFeature.objects.get(sampling_feature_uuid__exact=device.deployment_sampling_feature_uuid)
    #         feature_actions = sampling_feature.feature_actions.prefetch_related('results__timeseriesresult__values', 'results__variable').all()
    #         context['device_results'].append({'device': device, 'feature_actions': feature_actions})
    #     return context


class UserUpdateView(UpdateView):
    form_class = UserUpdateForm
    template_name = 'registration/account.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_form(self, form_class=None):
        user = self.get_object()
        organization = user.odm2user.affiliation.organization
        form = UserUpdateForm(instance=user, initial={'organization': organization})
        return form

    def get_hydroshare_account(self):
        hs_account = None
        if self.request.user.odm2user is not None:
            hs_account = self.request.user.odm2user.hydroshare_account
        return hs_account

    def get_context_data(self, **kwargs):
        context = super(UserUpdateView, self).get_context_data(**kwargs)
        context['hs_account'] = self.get_hydroshare_account()
        context['organization_form'] = OrganizationForm()
        return context

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return super(UserUpdateView, self).get(request, *args, **kwargs)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):

        if request.POST.get('disconnect-hydroshare-account'):
            odm2user = request.user.odm2user
            hs_acct_id = odm2user.hydroshare_account.pk
            odm2user.hydroshare_account = None
            HydroShareAccount.objects.get(pk=hs_acct_id).delete()
            odm2user.save()

            form = UserUpdateForm(instance=request.user, initial={'organization': request.user.odm2user.affiliation.organization})
            context = {
                'form': form,
                'organization_form': OrganizationForm(),
                'hs_accounts': None
            }
            return render(request, self.template_name, context=context)
        else:
            user = User.objects.get(pk=request.user.pk)
            form = UserUpdateForm(request.POST, instance=user,
                                  initial={'organization': user.odm2user.affiliation.organization})
            if form.is_valid():
                form.save()
                messages.success(request, 'Your information has been updated successfully.')
                return HttpResponseRedirect(reverse('user_account'))
            else:
                messages.error(request, 'There were some errors in the form.')
                return render(request, self.template_name, {'form': form, 'organization_form': OrganizationForm()})


class UserRegistrationView(CreateView):
    template_name = 'registration/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super(UserRegistrationView, self).get_context_data(**kwargs)
        context['organization_form'] = OrganizationForm()
        return context

    def post(self, request, *args, **kwargs):
        response = super(UserRegistrationView, self).post(request, *args, **kwargs)
        form = self.get_form()

        if form.instance.id:
            login(request, form.instance)

        return response


class SitesListView(LoginRequiredMixin, ListView):
    model = SiteRegistration
    context_object_name = 'sites'
    template_name = 'dataloaderinterface/my-sites.html'

    def get_queryset(self):
        return super(SitesListView, self).get_queryset()\
            .filter(django_user_id=self.request.user.id)\
            .prefetch_related('sensors')\
            .annotate(latest_measurement=Max('sensors__last_measurement_datetime'), latest_measurement_utc=Max('sensors__last_measurement_utc_datetime'))

    def get_context_data(self, **kwargs):
        context = super(SitesListView, self).get_context_data()
        context['followed_sites'] = self.request.user.followed_sites\
            .prefetch_related('sensors')\
            .annotate(latest_measurement=Max('sensors__last_measurement_utc_datetime'), latest_measurement_utc=Max('sensors__last_measurement_utc_datetime'))\
            .all()
        return context


class StatusListView(ListView):
    model = SiteRegistration
    context_object_name = 'sites'
    template_name = 'dataloaderinterface/status.html'

    def get_queryset(self):
        return super(StatusListView, self).get_queryset()\
            .filter(django_user_id=self.request.user.id)\
            .prefetch_related(Prefetch('sensors', queryset=SiteSensor.objects.filter(variable_code__in=[
                'EnviroDIY_Mayfly_Batt',
                'EnviroDIY_Mayfly_Temp'
            ]), to_attr='status_sensors')) \
            .annotate(latest_measurement=Max('sensors__last_measurement_utc_datetime'))\
            .order_by('sampling_feature_code')

    # noinspection PyArgumentList
    def get_context_data(self, **kwargs):
        context = super(StatusListView, self).get_context_data(**kwargs)
        context['followed_sites'] = self.request.user.followed_sites \
            .prefetch_related(Prefetch('sensors', queryset=SiteSensor.objects.filter(variable_code__in=[
                'EnviroDIY_Mayfly_Batt',
                'EnviroDIY_Mayfly_Temp'
            ]), to_attr='status_sensors')) \
            .annotate(latest_measurement=Max('sensors__last_measurement_utc_datetime'))\
            .order_by('sampling_feature_code')
        return context


class BrowseSitesListView(ListView):
    model = SiteRegistration
    context_object_name = 'sites'
    template_name = 'dataloaderinterface/browse-sites.html'

    def get_queryset(self):
        return super(BrowseSitesListView, self).get_queryset()\
            .prefetch_related('sensors').annotate(latest_measurement=Max('sensors__last_measurement_datetime'))


class SiteDetailView(DetailView):
    model = SiteRegistration
    context_object_name = 'site'
    slug_field = 'sampling_feature_code'
    slug_url_kwarg = 'sampling_feature_code'
    template_name = 'dataloaderinterface/site_details.html'

    def get_queryset(self):
        return super(SiteDetailView, self).get_queryset().prefetch_related('sensors')

    def get_context_data(self, **kwargs):
        context = super(SiteDetailView, self).get_context_data(**kwargs)
        context['tsa_url'] = settings.TSA_URL
        context['is_followed'] = self.request.user.is_authenticated and self.request.user.followed_sites.filter(sampling_feature_code=self.object.sampling_feature_code).exists()

        try:
            context["hydroshare_account"] = self.request.user.odm2user.hydroshare_account
        except AttributeError:
            pass

        try:
            resources = HydroShareResource.objects.filter(site_registration=context['site'].pk)
            context['resource_is_connected'] = len(resources) > 0
        except ObjectDoesNotExist:
            pass

        return context


class HydroShareResourceViewMixin:
    def __init__(self):
        self.request = None

    def get_hs_resource(self, resource):  # type: (HydroShareResource) -> Resource
        """ Creates a 'hydroshare_util.Resource' object """
        account = self.request.user.odm2user.hydroshare_account
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


class HydroShareResourceUpdateCreateView(UpdateView):
    slug_field = 'sampling_feature_code'

    def form_invalid(self, form):
        response = super(HydroShareResourceUpdateCreateView, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def get_object(self, queryset=None):
        site = SiteRegistration.objects.get(sampling_feature_code=self.kwargs[self.slug_field])
        try:
            resource = HydroShareResource.objects.get(site_registration=site.registration_id)
        except ObjectDoesNotExist:
            resource = None
        return resource

    def get_context_data(self, **kwargs):
        context = super(HydroShareResourceUpdateCreateView, self).get_context_data(**kwargs)
        context['date_format'] = settings.DATETIME_FORMAT
        return context

    def get(self, request, *args, **kwargs):
        # # uncomment to force a hydroshare resource file update.
        # # Only do this for debugging purposes!
        # call_command('update_hydroshare_resource_files', '--force-update')
        return super(HydroShareResourceUpdateCreateView, self).get(request, args, kwargs)


class HydroShareResourceCreateView(HydroShareResourceUpdateCreateView):
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

        context['site'] = site
        context['form'] = HydroShareSettingsForm(initial={'site_registration': site.pk,
                                                          'data_types': [initial_datatype],
                                                          'pause_sharing': False,
                                                          'title': self.generate_title(site),
                                                          'abstract': self.generate_abstract(site)})
        return context

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

            hs_account = self.request.user.odm2user.hydroshare_account

            resource = HydroShareResource(site_registration=site,
                                          hs_account=hs_account,
                                          data_types=",".join(form.cleaned_data['data_types']),
                                          update_freq=form.cleaned_data['update_freq'],
                                          sync_type=form.cleaned_data['schedule_type'],
                                          is_enabled=True,
                                          last_sync_date=timezone.now())

            token_json = hs_account.get_token()
            client = AuthUtil.authorize(token=token_json).get_client()
            hs_resource = Resource(client)

            hs_resource.owner = Resource.DEFAULT_OWNER
            hs_resource.resource_type = Resource.COMPOSITE_RESOURCE
            hs_resource.creator = '{0} {1}'.format(self.request.user.first_name, self.request.user.last_name)
            hs_resource.abstract = form.cleaned_data['abstract']
            hs_resource.title = form.cleaned_data['title']

            coverage = PointCoverage(name=site.sampling_feature_name, latitude=site.latitude, longitude=site.longitude)
            hs_resource.add_coverage(coverage)

            sensors = SiteSensor.objects.filter(registration=site)
            for sensor in sensors:
                hs_resource.keywords.add(sensor.variable_name)

            try:
                """
                NOTE: The UUID returned when creating a resource on hydroshare.org is externally generated and should only 
                be used as a reference to an external datasource that is not part of ODM2WebSDL database ecosystem.
                """
                resource.ext_id = hs_resource.create()
            except HydroShareHTTPException as e:
                return JsonResponse({"error": e.message,
                                     "message": "There was a problem with hydroshare.org and your resource was not created. You might want to see if www.hydroshare.org is working and try again later."},
                                    status=e.status_code)

            resource.save()

            # Upload data files to the newly created resource
            try:
                upload_hydroshare_resource_files(site, hs_resource)
            except Exception as e:
                # If the app fails here, the resource was created but the resource files failed to upload.
                logging.error('Failed to upload resource files: ' + e.message)
                pass

            success_url = reverse('site_detail', kwargs={'sampling_feature_code': site.sampling_feature_code})

            if self.request.is_ajax():
                return JsonResponse({'redirect': success_url})
            else:
                return redirect(success_url)
        else:
            return self.form_invalid(form)


class HydroShareResourceUpdateView(HydroShareResourceViewMixin, HydroShareResourceUpdateCreateView):
    template_name = 'hydroshare/hs_site_details.html'
    model = HydroShareResource
    slug_field = 'sampling_feature_code'
    slug_url_kwarg = 'hydroshare_settings_id'
    fields = '__all__'
    object = None

    def get_context_data(self, **kwargs):
        context = super(HydroShareResourceUpdateView, self).get_context_data(**kwargs)
        site = SiteRegistration.objects.get(sampling_feature_code=self.kwargs['sampling_feature_code'])
        hs_resource = self.get_object()
        context['site'] = site
        context['resource'] = hs_resource
        context['form'] = HydroShareSettingsForm(initial={
            'site_registration': site.pk,
            'update_freq': hs_resource.update_freq,
            'schedule_type': hs_resource.sync_type,
            'pause_sharing': not hs_resource.is_enabled,
            'data_types': hs_resource.data_types.split(",")
        })

        context['delete_form'] = HydroShareResourceDeleteForm()

        resource_util = self.get_hs_resource(hs_resource)
        try:
            resource_md = resource_util.get_system_metadata(timeout=10.0)
            context['resource_is_published'] = resource_md.get("published", False)
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
            resource_data = self.get_object()

            if 'update_files' in request.POST and resource_data.is_enabled:
                # get hydroshare resource info using hydroshare_util; this will get authentication info needed to
                # upload files to the resource.
                hs_resource = self.get_hs_resource(resource_data)

                # Upload the most recent resource files
                try:
                    upload_hydroshare_resource_files(site, hs_resource)
                except Exception as e:
                    return JsonResponse({'error': e.message}, status=500)

                # update last sync date on resource_data
                resource_data.last_sync_date = timezone.now()
            else:
                resource_data.data_types = ",".join(form.cleaned_data['data_types'])
                resource_data.update_freq = form.cleaned_data['update_freq']
                resource_data.sync_type = form.cleaned_data['schedule_type']
                resource_data.is_enabled = not form.cleaned_data["pause_sharing"]

            resource_data.save()

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

    def get_object(self, queryset=None):
        site = self.get_site_registration()
        try:
            resource = HydroShareResource.objects.get(site_registration=site.registration_id)
        except ObjectDoesNotExist:
            resource = None
        return site, resource

    def get(self, request, *arg, **kwargs):
        site = self.get_site_registration()
        return redirect(reverse('site_detail', kwargs={'sampling_feature_code': site.sampling_feature_code}))

    def post(self, request, *args, **kwargs):
        site, resource = self.get_object()

        form = HydroShareResourceDeleteForm(request.POST)
        if form.is_valid():
            delete_external_resource = form.cleaned_data.get('delete_external_resource')

            # delete resource in hydroshare.org if delete_external_resource is True
            if delete_external_resource is True:
                hs_resource = self.get_hs_resource(resource)
                try:
                    hs_resource.delete()
                except Exception as error:
                    print(error)

            # always delete the resource data stored on our server
            resource.delete()

        return redirect(reverse('site_detail', kwargs={'sampling_feature_code': site.sampling_feature_code}))


class SiteDeleteView(LoginRequiredMixin, DeleteView):
    model = SiteRegistration
    slug_field = 'sampling_feature_code'
    slug_url_kwarg = 'sampling_feature_code'
    success_url = reverse_lazy('sites_list')

    def post(self, request, *args, **kwargs):
        site = self.get_object(self.get_queryset())
        if not site:
            raise Http404

        if request.user.id != site.django_user_id and not self.request.user.is_staff:
            raise Http404

        try:
            hs_site = HydroShareResource.objects.get(site_registration=self.get_object())
            hs_site.delete()
        except ObjectDoesNotExist:
            pass

        sampling_feature = site.sampling_feature
        data_logger_program = DataLoggerProgramFile.objects.filter(
            affiliation_id=site.affiliation_id,
            program_name__contains=sampling_feature.sampling_feature_code
        ).first()
        data_logger_file = data_logger_program.data_logger_files.first()

        feature_actions = sampling_feature.feature_actions.with_results().all()
        for feature_action in feature_actions:
            result = feature_action.results.first()
            delete_result(result)

        data_logger_file.delete()
        data_logger_program.delete()
        sampling_feature.site.delete()
        sampling_feature.delete()
        site.sensors.all().delete()
        site.delete()
        return HttpResponseRedirect(self.success_url)

    def get(self, request, *args, **kwargs):
        raise Http404


class SiteUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'dataloaderinterface/site_registration.html'
    model = SiteRegistration
    slug_field = 'sampling_feature_code'
    slug_url_kwarg = 'sampling_feature_code'
    object = None
    fields = []

    def get_success_url(self):
        print 'Getting success url'
        return reverse_lazy('site_detail', kwargs={'sampling_feature_code': self.object.sampling_feature_code})

    def get_formset_initial_data(self, *args):
        # this shouldn't be here.
        if self.get_object().django_user != self.request.user and not self.request.user.is_staff:
            raise Http404

        registration = self.get_object()
        result_form_data = [
            {
                'result_id': sensor.result_id,
                'result_uuid': sensor.result_uuid,
                'equipment_model': sensor.equipment_model,
                'variable': sensor.variable,
                'unit': sensor.unit,
                'sampled_medium': sensor.medium
            }
            for sensor in registration.sensors.all()
        ]
        return result_form_data

    def get_hydroshare_accounts(self):
        try:
            return HydroShareAccount.objects.filter(user=self.request.user.id)
        except ObjectDoesNotExist:
            return []

    def get_context_data(self, **kwargs):
        if self.get_object().django_user != self.request.user and not self.request.user.is_staff:
            raise Http404
        context = super(SiteUpdateView, self).get_context_data()
        data = self.request.POST if self.request.POST else None
        sampling_feature = self.get_object().sampling_feature
        action_by = sampling_feature.feature_actions.first().action.action_by.first()

        site_alert = self.request.user.site_alerts\
            .filter(site_registration__sampling_feature_code=sampling_feature.sampling_feature_code)\
            .first()
        alert_data = {'notify': True, 'hours_threshold': int(site_alert.hours_threshold.total_seconds() / 3600)} if site_alert else {}

        context['sampling_feature_form'] = SamplingFeatureForm(data=data, instance=sampling_feature)
        context['site_form'] = SiteForm(data=data, instance=sampling_feature.site)
        context['results_formset'] = ResultFormSet(data=data, initial=self.get_formset_initial_data())
        context['action_by_form'] = ActionByForm(data=data, instance=action_by)
        context['email_alert_form'] = SiteAlertForm(data=data, initial=alert_data)
        context['zoom_level'] = data['zoom-level'] if data and 'zoom-level' in data else None
        return context

    def post(self, request, *args, **kwargs):
        if self.get_object().django_user != self.request.user and not self.request.user.is_staff:
            raise Http404
        site_registration = SiteRegistration.objects.filter(sampling_feature_code=self.kwargs['sampling_feature_code']).first()
        sampling_feature = site_registration.sampling_feature

        sampling_feature_form = SamplingFeatureForm(data=self.request.POST, instance=sampling_feature)
        site_form = SiteForm(data=self.request.POST, instance=sampling_feature.site)
        results_formset = ResultFormSet(data=self.request.POST, initial=self.get_formset_initial_data())
        action_by_form = ActionByForm(request.POST)
        notify_form = SiteAlertForm(request.POST)
        registration_form = self.get_form()

        if all_forms_valid(registration_form, sampling_feature_form, site_form, action_by_form, results_formset, notify_form):
            affiliation = action_by_form.cleaned_data['affiliation'] or request.user.odm2user.affiliation
            data_logger_file = DataLoggerFile.objects.filter(data_logger_file_name=site_registration.sampling_feature_code).first()
            data_logger_program = data_logger_file.program

            # Update notification settings
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

            # Update sampling feature
            sampling_feature_form.instance.save()

            # Update Site
            site_form.instance.save()

            # Update datalogger program and datalogger file names
            data_logger_program.program_name = '%s' % sampling_feature.sampling_feature_code
            data_logger_program.affiliation = affiliation
            data_logger_program.save()

            data_logger_file.data_logger_file_name = '%s' % sampling_feature.sampling_feature_code
            data_logger_file.save()

            # Update Site Registration
            site_registration.affiliation_id = affiliation.affiliation_id
            site_registration.django_user = User.objects.filter(odm2user__affiliation_id=affiliation.affiliation_id).first()
            site_registration.person = str(affiliation.person)
            site_registration.organization = str(affiliation.organization)
            site_registration.sampling_feature_code = sampling_feature.sampling_feature_code
            site_registration.sampling_feature_name = sampling_feature.sampling_feature_name
            site_registration.elevation_m = sampling_feature.elevation_m
            site_registration.latitude = sampling_feature.site.latitude
            site_registration.longitude = sampling_feature.site.longitude
            site_registration.site_type = sampling_feature.site.site_type_id
            registration_form.instance = site_registration
            site_registration.save()

            for result_form in results_formset.forms:
                is_new_result = 'result_id' not in result_form.initial
                to_delete = result_form['DELETE'].data

                if is_new_result and to_delete:
                    continue
                elif is_new_result:
                    create_result(site_registration, result_form, sampling_feature, affiliation, data_logger_file)
                    continue
                elif to_delete:
                    result = Result.objects.get(result_id=result_form.initial['result_id'])
                    delete_result(result)
                    continue

                # Update Result
                result = Result.objects.get(result_id=result_form.initial['result_id'])
                result.variable = result_form.cleaned_data['variable']
                result.sampled_medium = result_form.cleaned_data['sampled_medium']
                result.unit = result_form.cleaned_data['unit']
                result.save()

                # Update Data Logger file column
                instrument_output_variable = InstrumentOutputVariable.objects.filter(
                    model=result_form.cleaned_data['equipment_model'],
                    instrument_raw_output_unit=result.unit,
                    variable=result.variable,
                ).first()

                data_logger_file_column = result.data_logger_file_columns.first()
                data_logger_file_column.instrument_output_variable = instrument_output_variable
                data_logger_file_column.column_label = '%s(%s)' % (result.variable.variable_code, result.unit.unit_abbreviation)
                data_logger_file_column.save()

                # Update action by
                action_by = result.feature_action.action.action_by.first()
                action_by.affiliation = affiliation
                action_by.save()

                # Update Site Sensor
                site_sensor = SiteSensor.objects.filter(result_id=result.result_id).first()
                site_sensor.model_name = instrument_output_variable.model.model_name
                site_sensor.model_manufacturer = instrument_output_variable.model.model_manufacturer.organization_name
                site_sensor.variable_name = result.variable.variable_name_id
                site_sensor.variable_code = result.variable.variable_code
                site_sensor.unit_name = result.unit.unit_name
                site_sensor.unit_abbreviation = result.unit.unit_abbreviation
                site_sensor.sampled_medium = result.sampled_medium_id
                site_sensor.save()

            messages.success(request, 'The site has been updated successfully.')
            return self.form_valid(registration_form)
        else:
            messages.error(request, 'There are still some required fields that need to be filled out.')
            return self.form_invalid(registration_form)


class SiteRegistrationView(LoginRequiredMixin, CreateView):
    template_name = 'dataloaderinterface/site_registration.html'
    model = SiteRegistration
    object = None
    fields = []

    def get_success_url(self):
        return reverse_lazy('site_detail', kwargs={'sampling_feature_code': self.object.sampling_feature_code})

    @staticmethod
    def get_default_data():
        data = {
            'elevation_datum': ElevationDatum.objects.filter(pk='MSL').first(),
            'site_type': SiteType.objects.filter(pk='Stream').first()
        }
        return data

    def get_context_data(self, **kwargs):
        default_data = self.get_default_data()
        context = super(SiteRegistrationView, self).get_context_data()
        data = self.request.POST if self.request.POST else None
        context['sampling_feature_form'] = SamplingFeatureForm(data, initial=default_data)
        context['site_form'] = SiteForm(data, initial=default_data)
        context['results_formset'] = ResultFormSet(data)
        context['action_by_form'] = ActionByForm(data)
        context['email_alert_form'] = SiteAlertForm(data)
        context['zoom_level'] = data['zoom-level'] if data and 'zoom-level' in data else None
        return context

    def post(self, request, *args, **kwargs):
        sampling_feature_form = SamplingFeatureForm(request.POST)
        site_form = SiteForm(request.POST)
        results_formset = ResultFormSet(request.POST)
        action_by_form = ActionByForm(request.POST)
        notify_form = SiteAlertForm(request.POST)
        registration_form = self.get_form()

        if all_forms_valid(registration_form, sampling_feature_form, site_form, action_by_form, results_formset, notify_form):
            affiliation = action_by_form.cleaned_data['affiliation'] or request.user.odm2user.affiliation

            # Create sampling feature
            sampling_feature = sampling_feature_form.instance
            sampling_feature.sampling_feature_type_id = 'Site'
            sampling_feature.save()

            # Create Site
            site = site_form.instance
            site.sampling_feature = sampling_feature
            site.spatial_reference = SpatialReference.objects.get(srs_name='WGS84')
            site.save()

            # Create Data Logger file
            data_logger_program = DataLoggerProgramFile.objects.create(
                affiliation=affiliation,
                program_name='%s' % sampling_feature.sampling_feature_code
            )

            data_logger_file = DataLoggerFile.objects.create(
                program=data_logger_program,
                data_logger_file_name='%s' % sampling_feature.sampling_feature_code
            )

            # Create Site Registration TODO: maybe do it in another function.
            registration_data = {
                'registration_token': uuid4(),
                'registration_date': datetime.now(),
                'django_user': User.objects.filter(odm2user__affiliation_id=affiliation.affiliation_id).first(),
                'affiliation_id': affiliation.affiliation_id,
                'person': str(affiliation.person),
                'organization': str(affiliation.organization),
                'sampling_feature_id': sampling_feature.sampling_feature_id,
                'sampling_feature_code': sampling_feature.sampling_feature_code,
                'sampling_feature_name': sampling_feature.sampling_feature_name,
                'elevation_m': sampling_feature.elevation_m,
                'latitude': sampling_feature.site.latitude,
                'longitude': sampling_feature.site.longitude,
                'site_type': sampling_feature.site.site_type_id,
            }

            site_registration = SiteRegistration(**registration_data)
            registration_form.instance = site_registration
            site_registration.save()

            if notify_form.cleaned_data['notify']:
                self.request.user.site_alerts.create(
                    site_registration=site_registration,
                    hours_threshold=timedelta(hours=int(notify_form.data['hours_threshold']))
                )

            for result_form in results_formset.forms:
                create_result(site_registration, result_form, sampling_feature, affiliation, data_logger_file)

            return self.form_valid(registration_form)
        else:
            messages.error(request, 'There are still some required fields that need to be filled out!')
            return self.form_invalid(registration_form)


def all_forms_valid(*forms):
    return reduce(lambda all_valid, form: all_valid and form.is_valid(), forms, True)


def create_result(site_registration, result_form, sampling_feature, affiliation, data_logger_file):
    # Create action
    action = Action(
        method=Method.objects.filter(method_type_id='Instrument deployment').first(),
        action_type_id='Instrument deployment',
        begin_datetime=datetime.utcnow(), begin_datetime_utc_offset=0
    )
    action.save()

    # Create feature action
    feature_action = FeatureAction(action=action, sampling_feature=sampling_feature)
    feature_action.save()

    # Create action by
    action_by = ActionBy(action=action, affiliation=affiliation, is_action_lead=True)
    action_by.save()

    # Create Results
    result = result_form.instance
    result.feature_action = feature_action
    result.result_type_id = 'Time series coverage'
    result.processing_level = ProcessingLevel.objects.get(processing_level_code='Raw')
    result.status_id = 'Ongoing'
    result.save()

    # Create TimeSeriesResults
    time_series_result = TimeSeriesResult(result=result)
    time_series_result.aggregation_statistic_id = 'Average'
    time_series_result.save()

    # Create Data Logger file column
    instrument_output_variable = InstrumentOutputVariable.objects.filter(
        model=result_form.cleaned_data['equipment_model'],
        variable=result_form.cleaned_data['variable'],
        instrument_raw_output_unit=result_form.cleaned_data['unit'],
    ).first()

    DataLoggerFileColumn.objects.create(
        result=result,
        data_logger_file=data_logger_file,
        instrument_output_variable=instrument_output_variable,
        column_label='%s(%s)' % (result.variable.variable_code, result.unit.unit_abbreviation)
    )

    sensor_data = {
        'result_id': result.result_id,
        'result_uuid': result.result_uuid,
        'registration': site_registration,
        'model_name': instrument_output_variable.model.model_name,
        'model_manufacturer': instrument_output_variable.model.model_manufacturer.organization_name,
        'variable_name': result.variable.variable_name_id,
        'variable_code': result.variable.variable_code,
        'unit_name': result.unit.unit_name,
        'unit_abbreviation': result.unit.unit_abbreviation,
        'sampled_medium': result.sampled_medium_id
    }

    site_sensor = SiteSensor(**sensor_data)
    site_sensor.save()

    return result


class OAuthAuthorize(TemplateView):
    """handles the OAuth 2.0 authorization workflow with hydroshare.org"""
    def get(self, request, *args, **kwargs):
        if 'code' in request.GET:
            try:
                token_dict = AuthUtil.authorize_client_callback(request.GET['code'])  # type: dict
                auth_utility = AuthUtil.authorize(token=token_dict)  # type: AuthUtil
            except Exception as e:
                print 'Authorizition failure: {}'.format(e)
                return HttpResponse('Error: Authorization failure!')

            client = auth_utility.get_client()  # type: HydroShareAdapter
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

            request.user.odm2user.hydroshare_account = account
            request.user.odm2user.save()

            return redirect('user_account')
        elif 'error' in request.GET:
            return HttpResponseServerError(request.GET['error'])
        else:
            return AuthUtil.authorize_client()


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
        # Add 'redirect' as a url parameter
        url = reverse('hydroshare_oauth_redirect') + '?redirect=true'
        context['redirect_url'] = mark_safe(url)
        return context

    def get(self, request, *args, **kwargs):
        if 'redirect' in request.GET and request.GET['redirect'] == 'true':
            return AuthUtil.authorize_client()
        else:
            return super(OAuthRedirect, self).get(request, args, kwargs)


def delete_result(result):
    result_id = result.result_id
    feature_action = result.feature_action
    action = feature_action.action

    result.data_logger_file_columns.all().delete()
    result.timeseriesresult.values.all().delete()
    result.timeseriesresult.delete()

    action.action_by.all().delete()
    result.delete()

    feature_action.delete()
    action.delete()
    SiteSensor.objects.filter(result_id=result_id).delete()


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
