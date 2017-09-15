from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions

from dataloaderinterface.models import DeviceRegistration, SiteRegistration


class UUIDAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        if request.META['REQUEST_METHOD'] != 'POST':
            return None

        if 'HTTP_TOKEN' not in request.META:
            raise exceptions.ParseError("Registration Token not present in the request.")
        elif 'sampling_feature' not in request.data:
            raise exceptions.ParseError("Sampling feature UUID not present in the request.")

        # Get auth_token(uuid) from header, get registration object with auth_token, get the user from that registration, verify sampling_feature uuid is registered by this user, be happy.
        token = request.META['HTTP_TOKEN']
        registration = SiteRegistration.objects.filter(registration_token=token).first()
        if not registration:
            raise exceptions.PermissionDenied('Invalid Security Token')

        # request needs to have the sampling feature uuid of the registration -
        if str(registration.sampling_feature.sampling_feature_uuid) != request.data['sampling_feature']:
            raise exceptions.AuthenticationFailed(
                'Site Identifier is not associated with this Token')  # or other related exception

        return None
