from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView

from dataloader.models import FeatureAction


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


class DeviceRegistrationView(LoginRequiredMixin, FormView):
    pass


class DeviceUpdateView(LoginRequiredMixin, UpdateView):
    pass
