from django.conf.urls import url
from .views import OAuthAuthorize, OAuthAuthorizeRedirect

urlpatterns = [
    url(r'^$', OAuthAuthorize.as_view(), name='oauth'),
    url(r'authorize_redirect/', OAuthAuthorizeRedirect.as_view(), name='oauth_redirect')
]