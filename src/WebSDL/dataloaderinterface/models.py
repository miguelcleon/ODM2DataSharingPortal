from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class DeviceRegistration(models.Model):
    registration_id = models.AutoField(primary_key=True, db_column='RegistrationID')
    deployment_sampling_feature_uuid = models.UUIDField(db_column='SamplingFeatureUUID')
    authentication_token = models.CharField(max_length=64, editable=False, db_column='AuthToken')
    user = models.OneToOneField(User, db_column='User')
