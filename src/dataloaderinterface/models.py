from __future__ import unicode_literals

# Create your models here.
import uuid

from datetime import timedelta, datetime

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.db.models.aggregates import Min, Max

from dataloader.models import SamplingFeature, Affiliation, Result, TimeSeriesResultValue, EquipmentModel, Variable, \
    Unit, Medium
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings

from dataloaderinterface.querysets import SiteRegistrationQuerySet

HYDROSHARE_SYNC_TYPES = (('M', 'Manual'), ('S', 'Scheduled'))


class SiteRegistration(models.Model):
    registration_id = models.AutoField(primary_key=True, db_column='RegistrationID')
    registration_token = models.CharField(max_length=64, editable=False, db_column='RegistrationToken', unique=True)

    registration_date = models.DateTimeField(db_column='RegistrationDate')
    deployment_date = models.DateTimeField(db_column='DeploymentDate', blank=True, null=True)

    django_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='User', related_name='deployed_sites')
    affiliation_id = models.IntegerField(db_column='AffiliationID')

    person = models.CharField(max_length=765, db_column='Person')  # DEPRECATED

    person_id = models.IntegerField(db_column='PersonID', null=True)  # NEW: TEMPORARILY NULLABLE
    person_first_name = models.CharField(max_length=255, db_column='PersonFirstName', blank=True, null=True)  # NEW: TEMPORARILY NULLABLE
    person_last_name = models.CharField(max_length=255, db_column='PersonLastName', blank=True, null=True)  # NEW

    organization = models.CharField(max_length=255, db_column='Organization', blank=True, null=True)

    organization_id = models.IntegerField(db_column='OrganizationID', null=True)  # NEW
    organization_code = models.CharField(db_column='OrganizationCode', max_length=50, blank=True, null=True)  # NEW
    organization_name = models.CharField(max_length=255, db_column='OrganizationName', blank=True, null=True)  # NEW

    sampling_feature_id = models.IntegerField(db_column='SamplingFeatureID')
    sampling_feature_code = models.CharField(max_length=50, unique=True, db_column='SamplingFeatureCode')
    sampling_feature_name = models.CharField(max_length=255, blank=True, db_column='SamplingFeatureName')
    elevation_m = models.FloatField(blank=True, null=True, db_column='Elevation')

    latitude = models.FloatField(db_column='Latitude')
    longitude = models.FloatField(db_column='Longitude')
    site_type = models.CharField(max_length=765, db_column='SiteType')

    followed_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='followed_sites')
    alert_listeners = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='+', through='SiteAlert')

    objects = SiteRegistrationQuerySet.as_manager()

    @property
    def sampling_feature(self):
        return SamplingFeature.objects.get(pk=self.sampling_feature_id)

    @property
    def odm2_affiliation(self):
        return Affiliation.objects.get(pk=self.affiliation_id)

    def __str__(self):
        return '%s by %s from %s on %s' % (self.sampling_feature_code, self.person, self.organization, self.registration_date)

    def __repr__(self):
        return "<SiteRegistration('%s', '%s', '%s', '%s')>" % (
            self.registration_id, self.registration_date, self.sampling_feature_code, self.person
        )


class SensorMeasurement(models.Model):
    sensor = models.OneToOneField('SiteSensor', related_name='last_measurement', primary_key=True)
    value_datetime = models.DateTimeField()
    value_datetime_utc_offset = models.DurationField()
    data_value = models.FloatField()
    # measurement_local_datetime = models.DateTimeField(db_column='MeasurementUtcDatetime')

    @property
    def measurement_local_datetime(self):
        return

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

    def __str__(self):
        return '%s %s %s %s %s' % (self.model_manufacturer, self.model_name, self.variable_code, self.unit_name, self.sampled_medium)

    def __repr__(self):
        return "<SensorOutput('%s', [%s], ['%s'], ['%s'], ['%s'])>" % (
            self.pk, self.model_name, self.variable_code, self.unit_name, self.sampled_medium
        )


class SiteSensor(models.Model):
    registration = models.ForeignKey('SiteRegistration', db_column='RegistrationID', related_name='sensors')

    result_id = models.IntegerField(db_column='ResultID', unique=True)
    result_uuid = models.UUIDField(default=uuid.uuid4, editable=False, db_column='ResultUUID', unique=True)

    sensor_output = models.ForeignKey('SensorOutput', related_name='sensor_instances', null=True)  # NEW: TEMPORARILY NULLABLE

    model_name = models.CharField(db_column='ModelName', max_length=255)  # DEPRECATED
    model_manufacturer = models.CharField(db_column='ModelManufacturer', max_length=255)  # DEPRECATED

    variable_name = models.CharField(max_length=255, db_column='VariableName')  # DEPRECATED
    variable_code = models.CharField(max_length=50, db_column='VariableCode')  # DEPRECATED

    unit_name = models.CharField(max_length=255, db_column='UnitsName')  # DEPRECATED
    unit_abbreviation = models.CharField(max_length=255, db_column='UnitAbbreviation')  # DEPRECATED

    sampled_medium = models.CharField(db_column='SampledMedium', max_length=255)  # DEPRECATED

    last_measurement_id = models.IntegerField(db_column='LastMeasurementID', unique=True, blank=True, null=True)  # DEPRECATED
    last_measurement_value = models.FloatField(db_column='LastMeasurementValue', blank=True, null=True)  # DEPRECATED
    last_measurement_datetime = models.DateTimeField(db_column='LastMeasurementDatetime', blank=True, null=True)  # DEPRECATED
    last_measurement_utc_offset = models.IntegerField(db_column='LastMeasurementUtcOffset', blank=True, null=True)  # DEPRECATED
    last_measurement_utc_datetime = models.DateTimeField(db_column='LastMeasurementUtcDatetime', blank=True, null=True)  # DEPRECATED

    activation_date = models.DateTimeField(db_column='ActivationDate', blank=True, null=True)
    activation_date_utc_offset = models.IntegerField(db_column='ActivationDateUtcOffset', blank=True, null=True)

    class Meta:
        ordering = ['result_id']

    @property
    def result(self):
        return Result.objects.get(pk=self.result_id)

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
        return "{0}_{1}".format(self.model_manufacturer, self.model_name)

    @property
    def last_measurement(self):
        return TimeSeriesResultValue.objects.filter(pk=self.last_measurement_id).first()

    @property
    def sensor_identity(self):
        return "{0}_{1}_{2}".format(self.registration.sampling_feature_code, self.variable_code, self.result_id)

    @property
    def influx_url(self):
        if not self.last_measurement_id:
            return

        return settings.INFLUX_URL_QUERY.format(
            result_uuid=str(self.result_uuid).replace('-', '_'),
            last_measurement=self.last_measurement_datetime.strftime('%Y-%m-%dT%H:%M:%SZ'),
            days_of_data=settings.SENSOR_DATA_PERIOD
        )

    def __str__(self):
        return '%s %s' % (self.sensor_identity, self.unit_abbreviation)

    def __repr__(self):
        return "<SiteSensor('%s', [%s], '%s', '%s')>" % (
            self.id, self.registration, self.variable_code, self.unit_abbreviation,
        )


class ODM2User(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    affiliation_id = models.IntegerField()
    hydroshare_account = models.OneToOneField('HydroShareAccount', db_column='hs_account_id', null=True, blank=True)

    @property
    def affiliation(self):
        return Affiliation.objects.get(pk=self.affiliation_id)

    def can_administer_site(self, registration):
        return self.user.is_staff or registration.user == self

    class Meta:
        verbose_name = "ODM2 User"
        verbose_name_plural = "ODM2 Users"


class OAuthToken(models.Model):
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    token_type = models.CharField(max_length=len('Bearer'), default='Bearer', editable=False)
    expires_in = models.DateTimeField(default=timezone.now)
    scope = models.CharField(max_length=255, default='read')

    @property
    def is_expired(self):
        return datetime.today() > self.expires_in

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if isinstance(self.expires_in, str):
            self.expires_in = int(self.expires_in)

        if isinstance(self.expires_in, int):
            self.expires_in = datetime.today() + timedelta(seconds=self.expires_in)

        super(OAuthToken, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                     update_fields=update_fields)

    def to_dict(self):
        token = {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'token_type': self.token_type,
            'expires_in': int((self.expires_in - timezone.now()).total_seconds()),
            'scope': self.scope
        }
        return token

    class Meta:
        db_table = 'oauth_token'


# HSUAccount - holds information for user's Hydroshare account
class HydroShareAccount(models.Model):
    is_enabled = models.BooleanField(default=False)
    ext_id = models.IntegerField(unique=True)  # external hydroshare account id
    token = models.ForeignKey(OAuthToken, db_column='token_id', null=True, on_delete=models.CASCADE)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(HydroShareAccount, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                            update_fields=update_fields)

    @property
    def username(self):
        return ODM2User.objects.filter(hydroshare_account=self.pk).first().user.username

    def resources(self):
        return ", ".join([str(r.id) for r in HydroShareResource.objects.filter(hs_account=self)])
    resources.short_description = 'Resource IDs'

    def get_token(self):
        try:
            return self.token.to_dict()
        except ObjectDoesNotExist:
            return None

    def update_token(self, token_dict):  # type: (dict) -> None
        if isinstance(self.token, OAuthToken):
            self.token.access_token = token_dict.get('access_token')
            self.token.refresh_token = token_dict.get('refresh_token')
            self.token.token_type = token_dict.get('token_type')
            self.token.expires_in = token_dict.get('expires_in')
            self.token.scope = token_dict.get('scope')
            self.token.save()
        self.save()

    def to_dict(self, include_token=True):
        account = {
            'id': self.pk,
            'ext_id': self.ext_id,
            'is_enabled': self.is_enabled
        }
        if include_token:
            token = self.get_token()
            if token:
                account['token'] = token
        return account

    class Meta:
        db_table = 'hydroshare_account'


# "Settings" for a Hydroshare account connection
class HydroShareResource(models.Model):
    SYNC_TYPES = ['scheduled', 'manual']
    FREQUENCY_CHOICES = (
        (timedelta(), 'never'),
        (timedelta(minutes=1), 'minute'),
        (timedelta(days=1).total_seconds(), 'daily'),
        (timedelta(weeks=1).total_seconds(), 'weekly'),
        (timedelta(days=30).total_seconds(), 'monthly')
    )

    hs_account = models.ForeignKey(HydroShareAccount, db_column='hs_account_id', on_delete=models.CASCADE, null=True,
                                   blank=True)
    ext_id = models.CharField(max_length=255, blank=True, null=True, unique=True)  # external hydroshare resource id
    site_registration = models.OneToOneField(SiteRegistration, related_name='hydroshare_resource')
    sync_type = models.CharField(max_length=255, default='manual', choices=HYDROSHARE_SYNC_TYPES)
    update_freq = models.CharField(max_length=32, verbose_name='Update Frequency', default='daily')
    is_enabled = models.BooleanField(default=True)
    last_sync_date = models.DateTimeField(auto_created=True)
    data_types = models.CharField(max_length=255, blank=True, default='')
    visible = models.BooleanField(default=True)
    title = models.CharField(default='', blank=True, null=True, max_length=255)

    @property
    def sync_type_verbose(self):
        return 'Scheduled' if self.sync_type == 'S' else 'Manual'

    @property
    def update_freq_verbose(self):
        for choice in HydroShareResource.FREQUENCY_CHOICES:
            if choice[0] == self.update_freq.total_seconds():
                return choice[1]
        return 'NA'

    @property
    def next_sync_date(self):
        date = self.get_next_sync_date()
        if isinstance(date, datetime):
            return date.replace(hour=5, minute=0)
        return self.get_next_sync_date()

    @property
    def sync_at_hour(self):
        """
        :returns a string representation of the hour that files for this resource will sync at. For example, if
        sync_at_hour equals '5', then this resource will sync at 5:00 AM on days the resource fils are synced with
        hydroshare.org.
        """
        return str(settings.CRONTAB_EXECUTE_DAILY_AT_HOUR)

    def get_udpate_freq_index(self):
        try:
            return [choice[0] for choice in HydroShareResource.FREQUENCY_CHOICES].index(self.update_freq.total_seconds())
        except Exception:
            return 0

    def get_next_sync_date(self):
        days = 0
        minutes = 0
        if self.update_freq == 'minute':
            minutes = 1
        if self.update_freq == 'daily':
            days = 1
        elif self.update_freq == 'weekly':
            days = 7
        elif self.update_freq == 'monthly':
            days = 30

        if isinstance(self.last_sync_date, datetime):
            date = self.last_sync_date
        else:
            date = datetime.combine(self.last_sync_date.date(), datetime.min.time())

        return date + timedelta(days=days, minutes=minutes)

    def to_dict(self):
        return {
            'id': self.pk,
            'hs_account': self.hs_account.id,
            'site_registration': self.site_registration.registration_id,
            'sync_type': self.sync_type,
            'update_freq': self.update_freq,
            'is_enabled': self.is_enabled,
            'last_sync_date': self.last_sync_date,
            'data_types': self.data_types.split(",")
        }

    # def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
    #     return super(HydroShareResource, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return '<HydroShareResource: {}>'.format(self.pk)

    def __unicode__(self):
        return self.title if self.title is not None else self.ext_id

    class Meta:
        db_table = 'hydroshare_resource'


# HydroshareSyncLog - tracks scheduled or manual syncs with hydroshares API
class HydroShareSyncLog(models.Model):

    # HydroshareSiteSharing object this log belongs to
    site_sharing = models.ForeignKey(HydroShareResource, on_delete=models.CASCADE)

    # timestamp for when data was synced with Hydroshare.
    sync_date = models.DateTimeField(auto_now_add=True)

    # sync type, either 'manual' or 'scheduled'.
    sync_type = models.CharField(max_length=255, default='manual', choices=HYDROSHARE_SYNC_TYPES)

    # resultid corresponds to the PK in the `odm2` database on the `results.resultid` column.
    # resultid = models.IntegerField(db_column='odm2_results_resultid')

    class Meta:
        db_table = 'hydroshare_sync_log'


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
