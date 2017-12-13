from django.conf.urls import url
from .views import OAuthAuthorize

urlpatterns = [
    url(r'^$', OAuthAuthorize.as_view(), name='oauth')
]