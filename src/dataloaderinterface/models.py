from __future__ import unicode_literals

# Create your models here.
import uuid

from django.db.models.aggregates import Min

from dataloader.models import SamplingFeature, Affiliation, Result
from django.contrib.auth.models import User
from django.db import models


class SiteRegistration(models.Model):
    registration_id = models.AutoField(primary_key=True, db_column='RegistrationID')
    registration_token = models.CharField(max_length=64, editable=False, db_column='RegistrationToken', unique=True)

    registration_date = models.DateTimeField(db_column='RegistrationDate')
    deployment_date = models.DateTimeField(db_column='DeploymentDate', blank=True, null=True)

    django_user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='User', related_name='registrations')
    affiliation_id = models.IntegerField(db_column='AffiliationID')
    person = models.CharField(max_length=765, db_column='Person')
    organization = models.CharField(max_length=255, db_column='Organization', blank=True, null=True)

    sampling_feature_id = models.IntegerField(db_column='SamplingFeatureID')
    sampling_feature_code = models.CharField(max_length=50, unique=True, db_column='SamplingFeatureCode')
    sampling_feature_name = models.CharField(max_length=255, blank=True, db_column='SamplingFeatureName')
    elevation_m = models.FloatField(blank=True, null=True, db_column='Elevation')

    latitude = models.FloatField(db_column='Latitude')
    longitude = models.FloatField(db_column='Longitude')
    site_type = models.CharField(max_length=765, db_column='SiteType')

    followed_by = models.ManyToManyField(User, related_name='followed_sites')

    @property
    def sampling_feature(self):
        return SamplingFeature.objects.get(pk=self.sampling_feature_id)

    @property
    def odm2_affiliation(self):
        return Affiliation.objects.get(pk=self.affiliation_id)

    @property
    def deployment_date(self):
        min_datetime = self.sensors.aggregate(first_light=Min('activation_date'))
        return min_datetime['first_light']

    def __str__(self):
        return '%s by %s from %s on %s' % (self.sampling_feature_code, self.person, self.organization, self.registration_date)

    def __repr__(self):
        return "<SiteRegistration('%s', '%s', '%s', '%s')>" % (
            self.registration_id, self.registration_date, self.sampling_feature_code, self.person
        )


class SiteSensor(models.Model):
    registration = models.ForeignKey('SiteRegistration', db_column='RegistrationID', related_name='sensors')
    result_id = models.IntegerField(db_column='ResultID', unique=True)
    result_uuid = models.UUIDField(default=uuid.uuid4, editable=False, db_column='ResultUUID', unique=True)
    model_name = models.CharField(db_column='ModelName', max_length=255)
    model_manufacturer = models.CharField(db_column='ModelManufacturer', max_length=255)
    variable_name = models.CharField(max_length=255, db_column='VariableName')
    variable_code = models.CharField(max_length=50, db_column='VariableCode')
    unit_name = models.CharField(max_length=255, db_column='UnitsName')
    unit_abbreviation = models.CharField(max_length=255, db_column='UnitAbbreviation')
    sampled_medium = models.CharField(db_column='SampledMedium', max_length=255)
    activation_date = models.DateTimeField(db_column='ActivationDate', blank=True, null=True)
    activation_date_utc_offset = models.BigIntegerField(db_column='ActivationDateUtcOffset', blank=True, null=True)

    @property
    def make_model(self):
        return "{0}_{1}".format(self.model_manufacturer, self.model_name)

    @property
    def sensor_identity(self):
        return "{0}_{1}_{2}".format(self.registration.sampling_feature_code, self.variable_code, self.result_id)

    @property
    def result(self):
        return Result.objects.get(pk=self.result_id)

    def __str__(self):
        return '%s %s' % (self.variable_name, self.unit_abbreviation)

    def __repr__(self):
        return "<SiteSensor('%s', [%s], '%s', '%s')>" % (
            self.id, self.registration, self.variable_code, self.unit_abbreviation,
        )


class DeviceRegistration(models.Model):
    registration_id = models.AutoField(primary_key=True, db_column='RegistrationID')
    deployment_sampling_feature_uuid = models.UUIDField(db_column='SamplingFeatureUUID')
    authentication_token = models.CharField(max_length=64, editable=False, db_column='AuthenticationToken')
    user = models.ForeignKey('ODM2User', db_column='User')
    # deployment_date = models.DateTimeField(db_column='DeploymentDate')

    def registration_date(self):
        action = self.sampling_feature.actions.first()
        return action and action.begin_datetime

    @property
    def deployment_date(self):
        sampling_feature = self.sampling_feature
        min_datetime = sampling_feature.feature_actions.aggregate(first_light=Min('results__valid_datetime'))
        return min_datetime['first_light']

    @property
    def sampling_feature(self):
        return SamplingFeature.objects.get(sampling_feature_uuid__exact=self.deployment_sampling_feature_uuid)

    def __str__(self):
        action = self.sampling_feature.actions.first()
        return '{}\t{}: {}'.format(self.sampling_feature.sampling_feature_code, action.action_type_id, action.begin_datetime.strftime('%Y/%m/%d'))


class ODM2User(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    affiliation_id = models.IntegerField()

    @property
    def affiliation(self):
        return Affiliation.objects.get(pk=self.affiliation_id)

    def can_administer_site(self, registration):
        return self.user.is_staff or registration.user == self
