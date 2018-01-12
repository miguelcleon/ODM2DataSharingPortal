from django.conf.urls import url
from .views import OAuthAuthorize, OAuthAuthorizeRedirect, Resources, ResourceDetail

urlpatterns = [
    url(r'oauth/', OAuthAuthorize.as_view(), name='oauth'),
    url(r'authorize_redirect/', OAuthAuthorizeRedirect.as_view(), name='oauth_redirect'),
    url(r'resources/', Resources.as_view(), name='shared_resources'),
    url(r'resources/(?P<id>[a-zA-Z0-9]+)/', ResourceDetail.as_view(), name='resource')
]