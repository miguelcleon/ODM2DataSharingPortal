from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render

# Create your views here.
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView, CreateView
from django.views.generic.list import ListView

from dataloader.models import FeatureAction
from dataloaderinterface.forms import SamplingFeatureForm, ActionForm, ActionByForm, PeopleForm, OrganizationForm, \
    AffiliationForm, ResultFormSet
from dataloaderinterface.models import DeviceRegistration


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls):
        return login_required(super(LoginRequiredMixin, cls).as_view())


class HomeView(TemplateView):
    template_name = 'dataloaderinterface/index.html'


class DevicesListView(LoginRequiredMixin, ListView):
    model = FeatureAction
    template_name = 'dataloaderinterface/devices_list.html'


class DeviceDetailView(LoginRequiredMixin, DetailView):
    slug_field = 'feature_action_id'
    model = FeatureAction
    template_name = 'dataloaderinterface/device_detail.html'


class DeviceRegistrationView(LoginRequiredMixin, CreateView):
    template_name = 'dataloaderinterface/device_registration.html'
    model = DeviceRegistration
    fields = []

    def get_context_data(self, **kwargs):
        context = super(DeviceRegistrationView, self).get_context_data()
        context['sampling_feature_form'] = SamplingFeatureForm()
        context['action_form'] = ActionForm()
        context['action_by_form'] = ActionByForm()
        context['people_form'] = PeopleForm()
        context['organization_form'] = OrganizationForm()
        context['affiliation_form'] = AffiliationForm()
        context['results_formset'] = ResultFormSet()
        return context

    def get(self, request, *args, **kwargs):
        return super(DeviceRegistrationView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(DeviceRegistrationView, self).post(request, *args, **kwargs)


class DeviceUpdateView(LoginRequiredMixin, UpdateView):
    pass
