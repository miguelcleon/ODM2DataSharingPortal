from django.conf.urls import url

from .views import LeafPackCreateView, LeafPackDetailView, LeafPackDeleteView

urlpatterns = [
    url(r'(?P<uuid>.+)/delete/$', LeafPackDeleteView.as_view(), name='delete_leafpack'),
    url(r'(?P<uuid>.*)/$', LeafPackDetailView.as_view(), name='view_leafpack'),
    url(r'create/$', LeafPackCreateView.as_view(), name='create_leafpack'),
]
