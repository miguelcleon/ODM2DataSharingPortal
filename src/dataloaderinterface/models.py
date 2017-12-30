from __future__ import unicode_literals

# Create your models here.
import uuid

from datetime import timedelta, datetime

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.db.models.aggregates import Min

from dataloader.models import SamplingFeature, Affiliation, Result, TimeSeriesResultValue, EquipmentModel, Variable, \
    Unit, Medium
from django.contrib.auth.models import User
from django.db import models

HYDROSHARE_SYNC_TYPES = (('M', 'Manual'), ('S', 'Scheduled'))

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

    @property
    def last_measurements(self):
        if not self.deployment_date:
            return []

        measurement_ids = [long(measurement.last_measurement_id) for measurement in self.sensors.all() if measurement.last_measurement_id]
        measurements = TimeSeriesResultValue.objects.filter(pk__in=measurement_ids)
        return measurements

    @property
    def latest_measurement(self):
        if not self.deployment_date:
            return None
        return self.last_measurements.latest('value_datetime')

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
    last_measurement_id = models.IntegerField(db_column='LastMeasurementID', unique=True, blank=True, null=True)
    activation_date = models.DateTimeField(db_column='ActivationDate', blank=True, null=True)
    activation_date_utc_offset = models.IntegerField(db_column='ActivationDateUtcOffset', blank=True, null=True)

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
    def sensor_identity(self):
        return "{0}_{1}_{2}".format(self.registration.sampling_feature_code, self.variable_code, self.result_id)

    @property
    def last_measurement(self):
        return TimeSeriesResultValue.objects.filter(pk=self.last_measurement_id).first()

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


# HydroShareAccount - holds information for user's Hydroshare account
class HydroShareAccount(models.Model):
    user = models.ForeignKey('ODM2User', db_column='user_id')
    name = models.CharField(max_length=255, default='HydroShare Account')
    is_enabled = models.BooleanField(default=False)
    ext_hydroshare_id = models.IntegerField(unique=True)

    @classmethod
    def save_token(cls, token):
        if not isinstance(token, dict):
            raise TypeError("'token' must be of type 'dict'.")
        OAuthToken(cls, **token).save()

    @property
    def token(self):
        try:
            return OAuthToken.objects.get(account=self)
        except ObjectDoesNotExist:
            return None

    def to_dict(self, include_token=True):
        account = {
            'id': self.pk,
            'user_id': self.user.id,
            'name': self.name,
            'ext_hydroshare_id': self.ext_hydroshare_id,
            'is_enabled': self.is_enabled
        }
        if include_token:
            token = self.token
            if token:
                account['token'] = token.to_dict()
        return account

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'hydroshare_account'


# "Settings" for a Hydroshare account connection
class HydroShareSiteSetting(models.Model):
    FREQUENCY_CHOICES = (
        (timedelta(), 'Never'),
        (timedelta(hours=1).total_seconds(), 'Every Hour'),
        (timedelta(hours=3).total_seconds(), 'Every 3 Hours'),
        (timedelta(hours=6).total_seconds(), 'Every 6 Hours'),
        (timedelta(days=1).total_seconds(), 'Daily'),
        (timedelta(days=2).total_seconds(), 'Every 2 Days'),
        (timedelta(days=3).total_seconds(), 'Every 3 Days'),
        (timedelta(weeks=1).total_seconds(), 'Weekly'),
        (timedelta(weeks=2).total_seconds(), 'Bi Monthly'),
        (timedelta(days=30).total_seconds(), 'Monthly')
    )

    hs_account = models.ForeignKey(HydroShareAccount, db_column='hs_account_id', on_delete=models.CASCADE, null=True, blank=True)
    site_registration = models.OneToOneField(SiteRegistration, unique=True)
    sync_type = models.CharField(max_length=255, default='manual', choices=HYDROSHARE_SYNC_TYPES)
    resource_id = models.CharField(max_length=255, blank=True)
    update_freq = models.DurationField(verbose_name='Update Frequency', default=timedelta())
    is_enabled = models.BooleanField(default=False)
    last_sync_date = models.DateTimeField(blank=True, null=True)

    @property
    def sync_type_verbose(self):
        return 'Scheduled' if self.sync_type == 'S' else 'Manual'

    @property
    def update_freq_verbose(self):
        for choice in HydroShareSiteSetting.FREQUENCY_CHOICES:
            if choice[0] == self.update_freq.total_seconds():
                return choice[1]
        return 'NA'

    def get_udpate_freq_index(self):
        try:
            return [choice[0] for choice in HydroShareSiteSetting.FREQUENCY_CHOICES].index(self.update_freq.total_seconds())
        except Exception:
            return 0

    def to_dict(self):
        return {
            'id': self.pk,
            'hs_account': self.hs_account,
            'site_registration': self.site_registration,
            'sync_type': self.sync_type,
            'resource_id': self.resource_id,
            'update_freq': self.update_freq,
            'is_enabled': self.is_enabled,
            'last_sync_date': self.last_sync_date
        }

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        return super(HydroShareSiteSetting, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        db_table = 'hydroshare_site_setting'


# HydroshareSyncLog - tracks scheduled or manual syncs with hydroshares API
class HydroShareSyncLog(models.Model):

    # HydroshareSiteSharing object this log belongs to
    site_sharing = models.ForeignKey(HydroShareSiteSetting, on_delete=models.CASCADE)

    # timestamp for when data was synced with Hydroshare.
    sync_date = models.DateTimeField(auto_now_add=True)

    # sync type, either 'manual' or 'scheduled'.
    sync_type = models.CharField(max_length=255, default='manual', choices=HYDROSHARE_SYNC_TYPES)

    # resultid corresponds to the PK in the `odm2` database on the `results.resultid` column.
    # resultid = models.IntegerField(db_column='odm2_results_resultid')

    class Meta:
        db_table = 'hydroshare_sync_log'


class OAuthToken(models.Model):
    account = models.ForeignKey(HydroShareAccount, db_column='account_id')
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    token_type = models.CharField(max_length=len('Bearer'), default='Bearer', editable=False)
    expires_in = models.DateTimeField(default=timezone.now)
    scope = models.CharField(max_length=255, default='read')

    def __init__(self, *args, **kwargs):
        super(OAuthToken, self).__init__(args, kwargs)
        # Check if 'self.pk' exists. If not, the assumption is that this is a new token and
        # the 'expires_in' value needs to be converted into a datetime object representing
        # a future point in time when the token expires and will need to be refreshed.
        if not self.pk:
            if isinstance(self.expires_in, str):
                try:
                    self.expires_in = int(self.expires_in)
                    self.expires_in = datetime.today() + timedelta(seconds=self.expires_in)
                    # print(self.expires_in.strftime('%B %d, %Y, %I:%M:%S %p'))
                except ValueError as e:
                    raise ValueError("Failed to cast 'expires_in' from 'str' to 'int'.\n\t" + e.message)

    def to_dict(self, include_account=False):
        token = {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'token_type': self.token_type,
            'expires_in': int((self.expires_in - datetime.today()).total_seconds()),
            'scope': self.scope
        }
        if include_account:
            token['account'] = self.account.id
        return token

    class Meta:
        db_table = 'oauth_token'

