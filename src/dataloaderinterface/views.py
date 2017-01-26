from datetime import datetime
from uuid import uuid4

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models.query_utils import Q
from django.http.response import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django import http
from django.utils import six
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView, CreateView, ModelFormMixin
from django.views.generic.list import ListView

from dataloader.models import FeatureAction, SamplingFeatureType, ActionType, OrganizationType, Result, ResultType, \
    ProcessingLevel, Status, TimeSeriesResult, AggregationStatistic, SamplingFeature, Organization, SpatialReference, \
    ElevationDatum, SiteType, Affiliation, Medium, ActionBy, Action, Method
from dataloaderinterface.forms import SamplingFeatureForm, ResultFormSet, SiteForm, UserRegistrationForm, \
    OrganizationForm
from dataloaderinterface.models import DeviceRegistration


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls):
        return login_required(super(LoginRequiredMixin, cls).as_view())


class HomeView(TemplateView):
    template_name = 'dataloaderinterface/index.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data()
        context['device_results'] = []
        for device in DeviceRegistration.objects.get_queryset().filter(user=self.request.user.id):
            sampling_feature = SamplingFeature.objects.get(sampling_feature_uuid__exact=device.deployment_sampling_feature_uuid)
            feature_actions = sampling_feature.feature_actions.prefetch_related('results__timeseriesresult__values', 'results__variable').all()
            context['device_results'].append({'device': device, 'feature_actions': feature_actions})
        return context


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


class DevicesListView(LoginRequiredMixin, ListView):
    model = DeviceRegistration
    template_name = 'dataloaderinterface/my-sites.html'

    def get_queryset(self):
        return super(DevicesListView, self).get_queryset().filter(user_id=self.request.user.id)


class BrowseSitesListView(LoginRequiredMixin, ListView):
    model = SamplingFeature
    context_object_name = 'sites'
    template_name = 'dataloaderinterface/browse-sites.html'

    def get_queryset(self):
        return super(BrowseSitesListView, self).get_queryset().select_related('site').filter()


class DeviceDetailView(LoginRequiredMixin, DetailView):
    slug_field = 'registration_id'
    model = DeviceRegistration
    template_name = 'dataloaderinterface/device_detail.html'

    def get_context_data(self, **kwargs):
        context = super(DeviceDetailView, self).get_context_data()
        sampling_feature = SamplingFeature.objects.get(sampling_feature_uuid__exact=self.object.deployment_sampling_feature_uuid)
        context['sampling_feature'] = sampling_feature
        context['deployment'] = sampling_feature.actions.first()
        context['feature_actions'] = sampling_feature.feature_actions.prefetch_related('results__timeseriesresult__values', 'results__variable').all()
        context['affiliation'] = context['deployment'].action_by.first().affiliation
        context['site'] = sampling_feature.site
        return context


class DeviceRegistrationView(LoginRequiredMixin, CreateView):
    template_name = 'dataloaderinterface/device_registration.html'
    success_url = reverse_lazy('devices_list')
    model = DeviceRegistration
    object = None
    fields = []

    @staticmethod
    def get_default_data():
        data = {
            'elevation_datum': ElevationDatum.objects.filter(pk='MSL').first(),
            'site_type': SiteType.objects.filter(pk='Stream').first()
        }
        return data

    def get_context_data(self, **kwargs):
        default_data = self.get_default_data()
        context = super(DeviceRegistrationView, self).get_context_data()
        data = self.request.POST if self.request.POST else None
        context['sampling_feature_form'] = SamplingFeatureForm(data=data, initial=default_data)
        context['site_form'] = SiteForm(data=data, initial=default_data)
        context['results_formset'] = ResultFormSet(data=data, initial=[default_data])
        context['zoom_level'] = data['zoom-level'] if data and 'zoom-level' in data else None
        return context

    def post(self, request, *args, **kwargs):
        sampling_feature_form = SamplingFeatureForm(request.POST)
        site_form = SiteForm(request.POST)
        results_formset = ResultFormSet(request.POST)
        registration_form = self.get_form()

        if self.all_forms_valid(sampling_feature_form, site_form, results_formset):
            affiliation = request.user.odm2user.affiliation

            # Create sampling feature
            sampling_feature = sampling_feature_form.instance
            sampling_feature.sampling_feature_type_id = 'Site'
            sampling_feature.save()

            # Create Site
            site = site_form.instance
            site.sampling_feature = sampling_feature
            site.spatial_reference = SpatialReference.objects.get(srs_name='WGS84')
            site.save()

            for result_form in results_formset.forms:
                # Create action
                action = Action(
                    method=Method.objects.filter(method_type_id='Instrument deployment').first(),
                    action_type_id='Instrument deployment',
                    begin_datetime=datetime.now(), begin_datetime_utc_offset=-7
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

                # maybe create equipments and equipment used for actions so we can keep track of the equipment model
                # for when we implement the update form.
                # equipment fields:
                # code: whatever. an uuid maybe?
                # name: whatever. same as equipment model name maybe?
                # equipment type: Sensor
                # model id: result_form.cleaned_data['equipment model']
                # serial number: is it relevant?
                # owner: affiliation.
                # vendor: is it relevant?
                # purchase date: definitely not relevant.

            registration_form.instance.deployment_sampling_feature_uuid = sampling_feature.sampling_feature_uuid
            registration_form.instance.user_id = request.user.id
            registration_form.instance.authentication_token = uuid4()
            registration_form.instance.save()
            return self.form_valid(registration_form)
        else:
            messages.error(request, 'There are still some required fields that need to be filled out!')
            return self.form_invalid(registration_form)

    @staticmethod
    def all_forms_valid(*forms):
        return reduce(lambda all_valid, form: all_valid and form.is_valid(), forms, True)


class DeviceUpdateView(LoginRequiredMixin, UpdateView):
    pass
