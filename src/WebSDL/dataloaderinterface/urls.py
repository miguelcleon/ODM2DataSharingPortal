"""WebSDL URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from dataloaderinterface.views import DevicesListView, DeviceDetailView, DeviceRegistrationView, DeviceUpdateView

urlpatterns = [
    url(r'^devices/', DevicesListView.as_view(), name='devices_list'),
    url(r'^devices/(?P<slug>[-_\w]+)/$', DeviceDetailView.as_view(), name='device_detail'),
    url(r'^devices/register/$', DeviceRegistrationView.as_view(), name='device_registration'),
    url(r'^devices/register/update/(?P<slug>[-_\w]+)/$', DeviceUpdateView.as_view(), name='device_update'),
]
