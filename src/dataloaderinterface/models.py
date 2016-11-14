from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models


# Create your models here.
from dataloader.models import SamplingFeature


class DeviceRegistration(models.Model):
    registration_id = models.AutoField(primary_key=True, db_column='RegistrationID')
    deployment_sampling_feature_uuid = models.UUIDField(db_column='SamplingFeatureUUID')
    authentication_token = models.CharField(max_length=64, editable=False, db_column='AuthenticationToken')
    user = models.ForeignKey(User, db_column='User')

    def registration_date(self):
        sampling_feature = SamplingFeature.objects.using('odm2').get(
            sampling_feature_uuid__exact=self.deployment_sampling_feature_uuid)
        result = str(sampling_feature.feature_action.get().action).split(' ')
        d = result[3].replace('-', '/')
        t = result[4].split('+')[0]
        return d + ' ' + t

    def device_name(self):
        sampling_feature = SamplingFeature.objects.using('odm2').get(
                sampling_feature_uuid__exact=self.deployment_sampling_feature_uuid)
        return sampling_feature.sampling_feature_code

    def __str__(self):
        sampling_feature = SamplingFeature.objects.using('odm2').get(
                sampling_feature_uuid__exact=self.deployment_sampling_feature_uuid)
        result = str(sampling_feature.feature_action.get().action).split(' ')
        d = result[3].replace('-', '/')
        instr = '{}\t{} {}: {}'.format(sampling_feature.sampling_feature_code, result[0], result[1], d)

        return instr
