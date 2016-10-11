from datetime import datetime
from uuid import uuid4

from dal import autocomplete
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
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
    ProcessingLevel, Status, TimeSeriesResult, AggregationStatistic, SamplingFeature, Organization, SpatialReference
from dataloaderinterface.forms import SamplingFeatureForm, ActionForm, ActionByForm, PeopleForm, OrganizationForm, \
    AffiliationForm, ResultFormSet, SiteForm
from dataloaderinterface.models import DeviceRegistration


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls):
        return login_required(super(LoginRequiredMixin, cls).as_view())


class HomeView(TemplateView):
    template_name = 'dataloaderinterface/index.html'


class DevicesListView(LoginRequiredMixin, ListView):
    model = DeviceRegistration
    template_name = 'dataloaderinterface/devices_list.html'


class DeviceDetailView(LoginRequiredMixin, DetailView):
    slug_field = 'registration_id'
    model = DeviceRegistration
    template_name = 'dataloaderinterface/device_detail.html'

    def get_context_data(self, **kwargs):
        context = super(DeviceDetailView, self).get_context_data()
        sampling_feature = SamplingFeature.objects.get(sampling_feature_uuid__exact=self.object.deployment_sampling_feature_uuid)
        feature_action = sampling_feature.feature_action.first()

        context['sampling_feature'] = sampling_feature
        context['results'] = feature_action.result_set.all()
        context['deployment'] = feature_action.action
        context['affiliation'] = context['deployment'].action_by.first().affiliation
        context['site'] = sampling_feature.site
        return context


class DeviceRegistrationView(LoginRequiredMixin, CreateView):
    template_name = 'dataloaderinterface/device_registration.html'
    success_url = reverse_lazy('devices_list')
    model = DeviceRegistration
    object = None
    fields = []

    def get_context_data(self, **kwargs):
        context = super(DeviceRegistrationView, self).get_context_data()
        data = self.request.POST if self.request.POST else None
        context['sampling_feature_form'] = SamplingFeatureForm(data)
        context['site_form'] = SiteForm(data)
        context['action_form'] = ActionForm(data)
        context['action_by_form'] = ActionByForm(data)
        context['people_form'] = PeopleForm(data)
        context['organization_form'] = OrganizationForm(data)
        context['affiliation_form'] = AffiliationForm(data)
        context['results_formset'] = ResultFormSet(data)
        return context

    def post(self, request, *args, **kwargs):
        sampling_feature_form = SamplingFeatureForm(request.POST)
        action_form = ActionForm(request.POST)
        action_by_form = ActionByForm(request.POST)
        site_form = SiteForm(request.POST)
        # people_form = PeopleForm(request.POST)
        # organization_form = OrganizationForm(request.POST)
        # affiliation_form = AffiliationForm(request.POST)
        results_formset = ResultFormSet(request.POST)
        registration_form = self.get_form()

        if self.all_forms_valid(sampling_feature_form, site_form, action_form, action_by_form, results_formset):
            # Create sampling feature
            sampling_feature = sampling_feature_form.instance
            sampling_feature.sampling_feature_type = SamplingFeatureType.objects.get(name='Site')
            sampling_feature.save()

            # Create Site
            site = site_form.instance
            site.sampling_feature = sampling_feature
            site.spatial_reference = SpatialReference.objects.get(srs_name='WGS84')
            site.save()

            # Create action
            action = action_form.instance
            action.action_type = ActionType.objects.get(name='Instrument deployment')
            action.begin_datetime = datetime.now()
            action.begin_datetime_utc_offset = -7
            action.save()

            # Create feature action
            feature_action = FeatureAction(action=action, sampling_feature=sampling_feature)
            feature_action.save()

            # # Create person
            # person = people_form.instance
            # person.save()
            #
            # # Create organization
            # organization = organization_form.instance
            # organization.organization_type = OrganizationType.objects.get(name='Unknown')
            # organization.save()
            #
            # # Create affiliation
            # affiliation = affiliation_form.instance
            # affiliation.person = person
            # affiliation.organization = organization
            # affiliation.save()

            # Create action by
            action_by = action_by_form.instance
            action_by.action = action
            action_by.is_action_lead = True
            action_by.save()

            for result_data in results_formset.cleaned_data:
                if not result_data:
                    continue

                # Create Results
                result = Result(**result_data)
                result.feature_action = feature_action
                result.result_type = ResultType.objects.get(name='Time series coverage')
                # result.processing_level = ProcessingLevel.objects.get(processing_level_code='Raw')
                result.status = Status.objects.get(name='Ongoing')
                result.value_count = 0
                result.save()

                # Create TimeSeriesResults
                time_series_result = TimeSeriesResult(result=result)
                time_series_result.aggregation_statistic_cv = AggregationStatistic.objects.get(name='Average')
                time_series_result.save()

            registration_form.instance.deployment_sampling_feature_uuid = sampling_feature.sampling_feature_uuid
            registration_form.instance.user_id = self.request.user.id
            registration_form.instance.authentication_token = uuid4()
            registration_form.instance.save()
            return self.form_valid(registration_form)
        else:
            return self.form_invalid(registration_form)

    def all_forms_valid(self, *forms):
        return reduce(lambda all_valid, form: all_valid and form.is_valid(), forms, True)


class DeviceUpdateView(LoginRequiredMixin, UpdateView):
    pass
