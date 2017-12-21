from django.conf.urls import url
from .views import OAuthAuthorize, OAuthAuthorizeRedirect, Resources

urlpatterns = [
    url(r'oauth/', OAuthAuthorize.as_view(), name='oauth'),
    url(r'authorize_redirect/', OAuthAuthorizeRedirect.as_view(), name='oauth_redirect'),
    url(r'resources/(?P<id>[0-9]+)/', Resources.as_view(), name='resources')
]