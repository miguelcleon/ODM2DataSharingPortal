from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from .auth import OAuthUtil


class AuthMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super(AuthMiddleware, self).__init__(get_response)

        OAuthUtil._OAuthUtil__client_id = settings.HYDROSHARE_UTIL_CONFIG['CLIENT_ID']
        OAuthUtil._OAuthUtil__client_secret = settings.HYDROSHARE_UTIL_CONFIG['CLIENT_SECRET']
        OAuthUtil._OAuthUtil__redirect_uri = settings.HYDROSHARE_UTIL_CONFIG['REDIRECT_URI']
