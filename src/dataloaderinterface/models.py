from __future__ import unicode_literals

# Create your models here.
import uuid

from datetime import timedelta, datetime
from uuid import uuid4

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.db.models.aggregates import Min, Max

from dataloader.models import SamplingFeature, Affiliation, Result, TimeSeriesResultValue, EquipmentModel, Variable, \
    Unit, Medium
from django.db import models
from django.conf import settings
# from django.core.exceptions import ValidationError

from dataloaderinterface.querysets import SiteRegistrationQuerySet, SensorOutputQuerySet


class SiteRegistration(models.Model):
    registration_id = models.AutoField(primary_key=True, db_column='RegistrationID')
    registration_token = models.CharField(max_length=64, editable=False, db_column='RegistrationToken', unique=True, default=uuid4)

    registration_date = models.DateTimeField(db_column='RegistrationDate', default=datetime.utcnow)
    deployment_date = models.DateTimeField(db_column='DeploymentDate', blank=True, null=True)

    django_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='User', related_name='deployed_sites')
    affiliation_id = models.IntegerField(db_column='AffiliationID')

    person = models.CharField(max_length=765, db_column='Person')  # DEPRECATED

    person_id = models.IntegerField(db_column='PersonID', null=True)  # NEW: TEMPORARILY NULLABLE
    person_first_name = models.CharField(max_length=255, db_column='PersonFirstName', blank=True, null=True)  # NEW: TEMPORARILY NULLABLE
    person_last_name = models.CharField(max_length=255, db_column='PersonLastName', blank=True, null=True)  # NEW

    organization = models.CharField(max_length=255, db_column='Organization', blank=True, null=True)  # DEPRECATED

    organization_id = models.IntegerField(db_column='OrganizationID', null=True)  # NEW
    organization_code = models.CharField(db_column='OrganizationCode', max_length=50, blank=True, null=True)  # NEW
    organization_name = models.CharField(max_length=255, db_column='OrganizationName', blank=True, null=True)  # NEW

    sampling_feature_id = models.IntegerField(db_column='SamplingFeatureID', null=True)
    sampling_feature_code = models.CharField(max_length=50, unique=True, db_column='SamplingFeatureCode')
    sampling_feature_name = models.CharField(max_length=255, db_column='SamplingFeatureName')
    elevation_m = models.FloatField(blank=True, null=True, db_column='Elevation')
    elevation_datum = models.CharField(max_length=255, db_column='ElevationDatum', blank=True, null=True)

    latitude = models.FloatField(db_column='Latitude')
    longitude = models.FloatField(db_column='Longitude')
    site_type = models.CharField(max_length=255, db_column='SiteType')

    stream_name = models.CharField(max_length=255, db_column='StreamName', blank=True, null=True)
    major_watershed = models.CharField(max_length=255, db_column='MajorWatershed', blank=True, null=True)
    sub_basin = models.CharField(max_length=255, db_column='SubBasin', blank=True, null=True)
    closest_town = models.CharField(max_length=255, db_column='ClosestTown', blank=True, null=True)

    followed_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='followed_sites')
    alert_listeners = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='+', through='SiteAlert')

    objects = SiteRegistrationQuerySet.as_manager()

    @property
    def latest_measurement(self):
        if not hasattr(self, 'latest_measurement_id'):
            return
        try:
            last_updated_sensor = [sensor for sensor in self.sensors.all() if sensor.last_measurement.pk == self.latest_measurement_id].pop()
        except IndexError:
            return None

        return last_updated_sensor.last_measurement

    @property
    def sampling_feature(self):
        try:
            return SamplingFeature.objects.get(pk=self.sampling_feature_id)
        except ObjectDoesNotExist:
            return None

    @property
    def odm2_affiliation(self):
        try:
            return Affiliation.objects.get(pk=self.affiliation_id)
        except ObjectDoesNotExist:
            return None

    def __str__(self):
        return '%s' % self.sampling_feature_code

    def __repr__(self):
        return "<SiteRegistration('%s', '%s', '%s', '%s')>" % (
            self.registration_id, self.registration_date, self.sampling_feature_code, self.person
        )


class SensorMeasurement(models.Model):
    sensor = models.OneToOneField('SiteSensor', related_name='last_measurement', primary_key=True)
    value_datetime = models.DateTimeField()
    value_datetime_utc_offset = models.DurationField()
    data_value = models.FloatField()

    @property
    def value_local_datetime(self):
        return self.value_datetime + self.value_datetime_utc_offset

    @property
    def utc_offset_hours_display(self):
        total = int(self.value_datetime_utc_offset.total_seconds() / 3600)
        return "(UTC{sign}{hours}:00)".format(sign=["-", "+"][total > 0], hours=str(abs(self.utc_offset_hours)).zfill(2))

    @property
    def utc_offset_hours(self):
        return int(self.value_datetime_utc_offset.total_seconds() / 3600)

    def __str__(self):
        return '%s: %s' % (self.value_datetime, self.data_value)

    def __repr__(self):
        return "<SensorMeasurement('%s', %s, '%s', '%s')>" % (
            self.sensor, self.value_datetime, self.value_datetime_utc_offset, self.data_value
        )


class SensorOutput(models.Model):
    instrument_output_variable_id = models.IntegerField(db_index=True)

    model_id = models.IntegerField()
    model_name = models.CharField(max_length=255)
    model_manufacturer = models.CharField(max_length=255)

    variable_id = models.IntegerField()
    variable_name = models.CharField(max_length=255)
    variable_code = models.CharField(max_length=50)

    unit_id = models.IntegerField()
    unit_name = models.CharField(max_length=255)
    unit_abbreviation = models.CharField(max_length=255)

    sampled_medium = models.CharField(max_length=255, null=True)

    objects = SensorOutputQuerySet.as_manager()

    def __str__(self):
        return '%s %s %s %s %s' % (self.model_manufacturer, self.model_name, self.variable_code, self.unit_name, self.sampled_medium)

    def __repr__(self):
        return "<SensorOutput('%s', [%s], ['%s'], ['%s'], ['%s'])>" % (
            self.pk, self.model_name, self.variable_code, self.unit_name, self.sampled_medium
        )


class SiteSensor(models.Model):
    registration = models.ForeignKey('SiteRegistration', db_column='RegistrationID', related_name='sensors')

    result_id = models.IntegerField(db_column='ResultID', unique=True, null=True)
    result_uuid = models.UUIDField(db_column='ResultUUID', unique=True, null=True)

    sensor_output = models.ForeignKey('SensorOutput', related_name='sensor_instances', null=True)  # NEW: TEMPORARILY NULLABLE

    activation_date = models.DateTimeField(db_column='ActivationDate', blank=True, null=True)
    activation_date_utc_offset = models.IntegerField(db_column='ActivationDateUtcOffset', blank=True, null=True)

    model_name = models.CharField(db_column='ModelName', max_length=255, null=True)  # DEPRECATED
    model_manufacturer = models.CharField(db_column='ModelManufacturer', max_length=255, null=True)  # DEPRECATED

    variable_name = models.CharField(max_length=255, db_column='VariableName', null=True)  # DEPRECATED
    variable_code = models.CharField(max_length=50, db_column='VariableCode', null=True)  # DEPRECATED

    unit_name = models.CharField(max_length=255, db_column='UnitsName', null=True)  # DEPRECATED
    unit_abbreviation = models.CharField(max_length=255, db_column='UnitAbbreviation', null=True)  # DEPRECATED

    sampled_medium = models.CharField(db_column='SampledMedium', max_length=255, null=True)  # DEPRECATED

    last_measurement_id = models.IntegerField(db_column='LastMeasurementID', unique=True, blank=True, null=True)  # DEPRECATED
    last_measurement_value = models.FloatField(db_column='LastMeasurementValue', blank=True, null=True)  # DEPRECATED
    last_measurement_datetime = models.DateTimeField(db_column='LastMeasurementDatetime', blank=True, null=True)  # DEPRECATED
    last_measurement_utc_offset = models.IntegerField(db_column='LastMeasurementUtcOffset', blank=True, null=True)  # DEPRECATED
    last_measurement_utc_datetime = models.DateTimeField(db_column='LastMeasurementUtcDatetime', blank=True, null=True)  # DEPRECATED

    class Meta:
        ordering = ['result_id']

    @property
    def result(self):
        return Result.objects.filter(pk=self.result_id).first()

    @property
    def equipment_model(self):
        return EquipmentModel.objects.filter(model_name=self.model_name).first()

    @property
    def variable(self):
        return Variable.objects.filter(variable_code=self.variable_code).first()

    @property
    def unit(self):
        return Unit.objects.filter(unit_name=self.unit_name).first()

    @property
    def medium(self):
        return Medium.objects.filter(name=self.sampled_medium).first()

    @property
    def make_model(self):
        return "{0}_{1}".format(self.sensor_output.model_manufacturer, self.sensor_output.model_name)

    # @property
    # def last_measurement(self):
    #     return TimeSeriesResultValue.objects.filter(pk=self.last_measurement_id).first()

    @property
    def sensor_identity(self):
        return "{0}_{1}_{2}".format(self.registration.sampling_feature_code, self.variable_code, self.result_id)

    @property
    def influx_url(self):
        if not self.last_measurement:
            return

        return settings.INFLUX_URL_QUERY.format(
            result_uuid=str(self.result_uuid).replace('-', '_'),
            last_measurement=self.last_measurement.value_datetime.strftime('%Y-%m-%dT%H:%M:%SZ'),
            days_of_data=settings.SENSOR_DATA_PERIOD
        )

    def __str__(self):
        return '%s %s' % (self.sensor_identity, self.unit_abbreviation)

    def __repr__(self):
        return "<SiteSensor('%s', [%s], '%s')>" % (
            self.id, self.registration, self.result_id
        )


class ODM2User(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    affiliation_id = models.IntegerField()
    hydroshare_account = models.OneToOneField('hydroshare.HydroShareAccount', db_column='hs_account_id', null=True, blank=True)

    @property
    def affiliation(self):
        return Affiliation.objects.get(pk=self.affiliation_id)

    def can_administer_site(self, registration):
        return self.user.is_staff or registration.user == self

    class Meta:
        verbose_name = "ODM2 User"
        verbose_name_plural = "ODM2 Users"


class SiteAlert(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='User', related_name='site_alerts')
    site_registration = models.ForeignKey('SiteRegistration', db_column='RegistrationID', related_name='alerts')
    last_alerted = models.DateTimeField(db_column='LastAlerted', blank=True, null=True)
    hours_threshold = models.DurationField(db_column='HoursThreshold', default=timedelta(hours=1))

    def __str__(self):
        return '%s %s' % (self.site_registration.sampling_feature_code, self.hours_threshold)

    def __repr__(self):
        return "<SiteAlert('%s', [%s], '%s', '%s')>" % (
            self.id, self.site_registration.sampling_feature_code, self.last_alerted, self.hours_threshold,
        )
