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

from dataloaderinterface.views import SitesListView, SiteDetailView, SiteRegistrationView, \
    HomeView, BrowseSitesListView, SiteUpdateView, SiteDeleteView, StatusListView, HydroShareResourceUpdateView, \
    HydroShareResourceCreateView

urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^sites/$', SitesListView.as_view(), name='sites_list'),
    url(r'^status/$', StatusListView.as_view(), name='status'),
    url(r'^browse/$', BrowseSitesListView.as_view(), name='browse_sites'),
    url(r'^sites/register/$', SiteRegistrationView.as_view(), name='site_registration'),
    url(r'^sites/update/(?P<sampling_feature_code>.*)/$', SiteUpdateView.as_view(), name='site_update'),
    url(r'^sites/delete/(?P<sampling_feature_code>.*)/$', SiteDeleteView.as_view(), name='site_delete'),
    url(r'^sites/(?P<sampling_feature_code>.*)/hsr/create/$', HydroShareResourceCreateView.as_view(), name='hs_resource_create'),
    url(r'^sites/(?P<sampling_feature_code>.*)/hsr/update/$', HydroShareResourceUpdateView.as_view(), name='hs_resource_update'),
    url(r'^sites/(?P<sampling_feature_code>.*)/$', SiteDetailView.as_view(), name='site_detail'),
]
