from django.shortcuts import render

# Create your views here.
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView

from dataloader.models import FeatureAction


class DevicesListView(ListView):
    model = FeatureAction
    template_name = 'dataloaderinterface/devices_list.html'


class DeviceDetailView(DetailView):
    slug_field = 'feature_action_id'
    model = FeatureAction
    template_name = 'dataloaderinterface/device_detail.html'


class DeviceRegistrationView(FormView):
    pass


class DeviceUpdateView(UpdateView):
    pass
