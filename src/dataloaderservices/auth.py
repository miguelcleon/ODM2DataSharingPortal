from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions

from dataloaderinterface.models import DeviceRegistration


class UUIDAuthentication(authentication.BaseAuthentication):
	def authenticate(self, request):
		# TODO: Get auth_token(uuid) from header, get registration object with auth_token, get the user from that registration, verify sampling_feature uuid is registered by this user, be happy.
		token = request.META['HTTP_TOKEN']
		registration_queryset = DeviceRegistration.objects.using('default').filter(authentication_token=token)
		if not registration_queryset.exists():
			raise exceptions.PermissionDenied('Invalid Security Token')
		registration = registration_queryset.get()
		
		# request needs to have the sampling feature uuid of the registration - TODO: there's probably a better way of comparing this
		if str(registration.deployment_sampling_feature_uuid) != request.data['sampling_feature']:
			raise exceptions.AuthenticationFailed('Invalid Site Identifier')  # or other related exception
			
		# TODO: probably log user in? (registration.user)
		return None
