from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models


# Create your models here.
from dataloader.models import SamplingFeature, Affiliation


class DeviceRegistration(models.Model):
    registration_id = models.AutoField(primary_key=True, db_column='RegistrationID')
    deployment_sampling_feature_uuid = models.UUIDField(db_column='SamplingFeatureUUID')
    authentication_token = models.CharField(max_length=64, editable=False, db_column='AuthenticationToken')
    user = models.ForeignKey('ODM2User', db_column='User')

    @property
    def sampling_feature(self):
        return SamplingFeature.objects.get(sampling_feature_uuid__exact=self.deployment_sampling_feature_uuid)

    def registration_date(self):
        return self.sampling_feature.actions.first().begin_datetime.strftime('%Y/%m/%d %H:%M:%S')

    def device_name(self):
        sampling_feature = SamplingFeature.objects.using('odm2').get(
                sampling_feature_uuid__exact=self.deployment_sampling_feature_uuid)

        if sampling_feature.sampling_feature_name is not None and len(sampling_feature.sampling_feature_name) > 0:
            return sampling_feature.sampling_feature_code + ' at ' + sampling_feature.sampling_feature_name

        return sampling_feature.sampling_feature_code

    def __str__(self):
        action = self.sampling_feature.actions.first()
        return '{}\t{}: {}'.format(self.sampling_feature.sampling_feature_code, action.action_type_id, action.begin_datetime.strftime('%Y/%m/%d'))


class ODM2User(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    affiliation_id = models.IntegerField()

    @property
    def affiliation(self):
        return Affiliation.objects.get(pk=self.affiliation_id)
