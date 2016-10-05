from __future__ import unicode_literals
import uuid

from django.db import models

# TODO: import settings and get dbs, use reflection to add schema name depending on the type of database.


# Controlled Vocabularies

class ControlledVocabulary(models.Model):
    term = models.CharField(db_column='term', max_length=255)
    name = models.CharField(db_column='name', primary_key=True, max_length=255)
    definition = models.CharField(db_column='definition', blank=True, max_length=500)
    category = models.CharField(db_column='category', blank=True, max_length=255)
    source_vocabulary_uri = models.CharField(db_column='sourcevocabularyuri', blank=True, max_length=255)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True


class SamplingFeatureType(ControlledVocabulary):
    class Meta:
        db_table = 'cv_samplingfeaturetype'


class SiteType(ControlledVocabulary):
    class Meta:
        db_table = 'cv_sitetype'


class ElevationDatum(ControlledVocabulary):
    class Meta:
        db_table = 'cv_elevationdatum'


class ActionType(ControlledVocabulary):
    class Meta:
        db_table = 'cv_actiontype'


class MethodType(ControlledVocabulary):
    class Meta:
        db_table = 'cv_methodtype'


class OrganizationType(ControlledVocabulary):
    class Meta:
        db_table = 'cv_organizationtype'


class ResultType(ControlledVocabulary):
    class Meta:
        db_table = 'cv_resulttype'


class Medium(ControlledVocabulary):
    class Meta:
        db_table = 'cv_medium'


class AggregationStatistic(ControlledVocabulary):
    class Meta:
        db_table = 'cv_aggregationstatistic'


class CensorCode(ControlledVocabulary):
    class Meta:
        db_table = 'cv_censorcode'


class Status(ControlledVocabulary):
    class Meta:
        db_table = 'cv_status'


class UnitType(ControlledVocabulary):
    class Meta:
        db_table = 'cv_unittype'


class QualityCode(ControlledVocabulary):
    class Meta:
        db_table = 'cv_qualitycode'


class VariableType(ControlledVocabulary):
    class Meta:
        db_table = 'cv_variabletype'


class VariableName(ControlledVocabulary):
    class Meta:
        db_table = 'cv_variablename'


# ODM2 Core models

class SamplingFeature(models.Model):
    sampling_feature_id = models.AutoField(db_column='samplingfeatureid', primary_key=True)
    sampling_feature_uuid = models.UUIDField(default=uuid.uuid4, editable=False, db_column='samplingfeatureuuid')
    sampling_feature_type = models.ForeignKey('SamplingFeatureType', db_column='samplingfeaturetypecv')
    sampling_feature_code = models.CharField(db_column='samplingfeaturecode', max_length=50)
    sampling_feature_name = models.CharField(db_column='samplingfeaturename', blank=True, max_length=255)
    sampling_feature_description = models.CharField(db_column='samplingfeaturedescription', blank=True, max_length=500)
    elevation_m = models.FloatField(db_column='elevation_m', blank=True, null=True)
    elevation_datum = models.ForeignKey('ElevationDatum', db_column='elevationdatumcv', blank=True, null=True)

    def __str__(self):
        return str(self.sampling_feature_type_id) + ': ' + self.sampling_feature_code + ' ' + self.sampling_feature_name

    def __unicode__(self):
        return unicode(self.sampling_feature_type_id) + ': ' + self.sampling_feature_code + ' ' + self.sampling_feature_name

    class Meta:
        db_table = 'samplingfeatures'


class SpatialReference(models.Model):
    spatial_reference = models.AutoField(db_column='spatialreferenceid', primary_key=True)
    srs_code = models.CharField(db_column='srscode', blank=True, max_length=50)
    srs_name = models.CharField(db_column='srsname', max_length=255)
    srs_description = models.CharField(db_column='srsdescription', blank=True, max_length=500)

    def __str__(self):
        return self.srsname

    def __unicode__(self):
        return self.srsname

    class Meta:
        db_table = 'spatialreferences'


class Site(models.Model):
    sampling_feature = models.OneToOneField('SamplingFeature', related_name='site', db_column='samplingfeatureid', primary_key=True)
    site_type = models.ForeignKey('SiteType', db_column='sitetypecv')
    latitude = models.FloatField(db_column='latitude')
    longitude = models.FloatField(db_column='longitude')
    spatial_reference = models.ForeignKey('SpatialReference', db_column='spatialreferenceid')

    class Meta:
        db_table = 'sites'


class FeatureAction(models.Model):
    feature_action_id = models.AutoField(db_column='featureactionid', primary_key=True)
    sampling_feature = models.ForeignKey('SamplingFeature', related_name="feature_action", db_column='samplingfeatureid')
    action = models.ForeignKey('Action', related_name="feature_action", db_column='actionid')

    def __str__(self):
        return str(self.action) + ' ' + self.sampling_feature.sampling_feature_code + ' (' + str(self.sampling_feature.sampling_feature_type) + ')'

    def __unicode__(self):
        return unicode(self.action) + ' ' + self.sampling_feature.sampling_feature_code + ' (' + unicode(self.sampling_feature.sampling_feature_type) + ')'

    class Meta:
        db_table = 'featureactions'


class Action(models.Model):
    action_id = models.AutoField(db_column='actionid', primary_key=True)
    action_type = models.ForeignKey('ActionType', db_column='actiontypecv')
    method = models.ForeignKey('Method', db_column='methodid')
    begin_datetime = models.DateTimeField(db_column='begindatetime')
    begin_datetime_utc_offset = models.IntegerField(db_column='begindatetimeutcoffset')
    action_description = models.TextField(db_column='actiondescription', blank=True)

    def __str__(self):
        return str(self.action_type_id) + ' - ' + str(self.begin_datetime) + ' ' + str(self.begin_datetime_utc_offset)

    def __unicode__(self):
        return unicode(self.action_type_id) + ' - ' + unicode(self.begin_datetime) + ' ' + unicode(self.begin_datetime_utc_offset)

    class Meta:
        db_table = 'actions'


class ActionBy(models.Model):
    bridge_id = models.AutoField(db_column='bridgeid', primary_key=True)
    action = models.ForeignKey('Action', related_name="action_by", db_column='actionid')
    affiliation = models.ForeignKey('Affiliation', db_column='affiliationid')
    is_action_lead = models.BooleanField(db_column='isactionlead', default=None)
    role_description = models.CharField(db_column='roledescription', blank=True, max_length=255)

    def __str__(self):
        return str(self.action) + ': ' + str(self.affiliation)

    def __unicode__(self):
        return unicode(self.action) + ': ' + unicode(self.affiliation)

    class Meta:
        db_table = 'actionby'


class Method(models.Model):
    method_id = models.AutoField(db_column='methodid', primary_key=True)
    method_type = models.ForeignKey('MethodType', db_column='methodtypecv')
    method_code = models.CharField(db_column='methodcode', max_length=50)
    method_name = models.CharField(db_column='methodname', max_length=255)
    method_description = models.CharField(db_column='methoddescription', blank=True, max_length=500)
    method_link = models.CharField(db_column='methodlink', blank=True, max_length=255)
    organization = models.ForeignKey('Organization', db_column='organizationid', blank=True, null=True)

    def __str__(self):
        return str(self.method_type_id) + ': ' + self.method_name

    def __unicode__(self):
        return unicode(self.method_type_id) + ': ' + self.method_name

    class Meta:
        db_table = 'methods'


class People(models.Model):
    person_id = models.AutoField(db_column='personid', primary_key=True)
    person_first_name = models.CharField(db_column='personfirstname', max_length=255)
    person_middle_name = models.CharField(db_column='personmiddlename', blank=True, max_length=255)
    person_last_name = models.CharField(db_column='personlastname', max_length=255)

    def __str__(self):
        return self.person_first_name + ' ' + self.person_last_name

    def __unicode__(self):
        return self.person_first_name + ' ' + self.person_last_name

    class Meta:
        db_table = 'people'


class Organization(models.Model):
    organization_id = models.AutoField(db_column='organizationid', primary_key=True)
    organization_type = models.ForeignKey('OrganizationType', db_column='organizationtypecv')
    organization_code = models.CharField(db_column='organizationcode', max_length=50)
    organization_name = models.CharField(db_column='organizationname', max_length=255)
    organization_description = models.CharField(db_column='organizationdescription', blank=True, max_length=500)
    organization_link = models.CharField(db_column='organizationlink', blank=True, max_length=255)
    parent_organization = models.ForeignKey('self', db_column='parentorganizationid', blank=True, null=True)

    def __str__(self):
        return str(self.organization_type_id) + ': ' + self.organization_name

    def __unicode__(self):
        return unicode(self.organization_type_id) + ': ' + self.organization_name

    class Meta:
        db_table = 'organizations'


class Affiliation(models.Model):
    affiliation_id = models.AutoField(db_column='affiliationid', primary_key=True)
    person = models.ForeignKey('People', related_name='affiliation', db_column='personid')
    organization = models.ForeignKey('Organization', related_name='affiliation', db_column='organizationid', blank=True, null=True)
    is_primary_organization_contact = models.NullBooleanField(db_column='isprimaryorganizationcontact', default=None)
    affiliation_start_date = models.DateField(db_column='affiliationstartdate')
    affiliation_end_date = models.DateField(db_column='affiliationenddate', blank=True, null=True)
    primary_phone = models.CharField(db_column='primaryphone', blank=True, max_length=50)
    primary_email = models.CharField(db_column='primaryemail', max_length=255)
    primary_address = models.CharField(db_column='primaryaddress', blank=True, max_length=255)
    person_link = models.CharField(db_column='personlink', blank=True, max_length=255)

    def __str__(self):
        return str(self.person) + ' (' + self.organization.organization_name + ')'

    def __unicode__(self):
        return unicode(self.person) + ' (' + self.organization.organization_name + ')'

    class Meta:
        db_table = 'affiliations'


class ProcessingLevel(models.Model):
    processing_level_id = models.AutoField(db_column='processinglevelid', primary_key=True)
    processing_level_code = models.CharField(db_column='processinglevelcode', max_length=50)
    definition = models.CharField(db_column='definition', blank=True, max_length=500)
    explanation = models.CharField(db_column='explanation', blank=True, max_length=500)

    def __str__(self):
        return self.processing_level_code + ' (' + self.definition + ')'

    def __unicode__(self):
        return self.processing_level_code + ' (' + self.definition + ')'

    class Meta:
        db_table = 'processinglevels'


class Unit(models.Model):
    unit_id = models.AutoField(db_column='unitsid', primary_key=True)
    unit_type = models.ForeignKey('UnitType', db_column='unitstypecv')
    unit_abbreviation = models.CharField(db_column='unitsabbreviation', max_length=255)
    unit_name = models.CharField(db_column='unitsname', max_length=255)

    def __str__(self):
        return str(self.unit_type_id) + ': ' + self.unit_abbreviation + ' (' + self.unit_name + ')'

    def __unicode__(self):
        return unicode(self.unit_type_id) + ': ' + self.unit_abbreviation + ' (' + self.unit_name + ')'

    class Meta:
        db_table = 'units'


class Variable(models.Model):
    variable_id = models.AutoField(db_column='variableid', primary_key=True)
    variable_type = models.ForeignKey('VariableType', db_column='variabletypecv')
    variable_code = models.CharField(db_column='variablecode', max_length=50)
    variable_name = models.ForeignKey('VariableName', db_column='variablenamecv')
    variable_definition = models.CharField(db_column='variabledefinition', blank=True, max_length=255)
    no_data_value = models.FloatField(db_column='nodatavalue')

    def __str__(self):
        return str(self.variable_name) + ': ' + self.variable_code + ' (' + str(self.variable_type_id) + ')'

    def __unicode__(self):
        return unicode(self.variable_name) + ': ' + self.variable_code + ' (' + unicode(self.variable_type_id) + ')'

    class Meta:
        db_table = 'variables'


class Result(models.Model):
    result_id = models.AutoField(db_column='resultid', primary_key=True)
    result_uuid = models.CharField(db_column='resultuuid', default=uuid.uuid4, max_length=255)
    feature_action = models.ForeignKey('FeatureAction', db_column='featureactionid')
    result_type = models.ForeignKey('ResultType', db_column='resulttypecv')
    variable = models.ForeignKey('Variable', db_column='variableid')
    unit = models.ForeignKey('Unit', db_column='unitsid')
    processing_level = models.ForeignKey(ProcessingLevel, db_column='processinglevelid')
    result_datetime = models.DateTimeField(db_column='resultdatetime', blank=True, null=True)
    result_datetime_utc_offset = models.BigIntegerField(db_column='resultdatetimeutcoffset', blank=True, null=True)
    status = models.ForeignKey('Status', db_column='statuscv', blank=True)
    sampled_medium = models.ForeignKey('Medium', db_column='sampledmediumcv')
    value_count = models.IntegerField(db_column='valuecount')

    def __str__(self):
        return str(self.result_datetime) + ' - ' + str(self.result_type_id) + ' (' + str(self.variable.variable_name_id) + '): ' + self.variable.variable_code + ' ' + self.unit.unit_abbreviation

    def __unicode__(self):
        return unicode(self.result_datetime) + ' - ' + unicode(self.result_type_id) + ' (' + unicode(self.variable.variable_name_id) + '): ' + self.variable.variable_code + ' ' + self.unit.unit_abbreviation

    class Meta:
        db_table = 'results'


class TimeSeriesResult(models.Model):
    result = models.OneToOneField(Result, db_column='resultid', primary_key=True)
    x_location = models.FloatField(db_column='xlocation', blank=True, null=True)
    x_location_unit = models.ForeignKey('Unit', related_name='time_series_x_locations', db_column='xlocationunitsid', blank=True, null=True)
    y_location = models.FloatField(db_column='ylocation', blank=True, null=True)
    y_location_unit = models.ForeignKey('Unit', related_name='time_series_y_locations', db_column='ylocationunitsid', blank=True, null=True)
    z_location = models.FloatField(db_column='zlocation', blank=True, null=True)
    z_location_unit = models.ForeignKey('Unit', related_name='time_series_z_locations', db_column='zlocationunitsid', blank=True, null=True)
    intended_time_spacing = models.FloatField(db_column='intendedtimespacing', blank=True, null=True)
    intended_time_spacing_unit = models.ForeignKey('Unit', related_name='time_series_intended_time_spacing', db_column='intendedtimespacingunitsid', blank=True, null=True)
    aggregation_statistic_cv = models.ForeignKey('AggregationStatistic', db_column='aggregationstatisticcv')

    def __str__(self):
        return str(self.result)

    def __unicode__(self):
        return unicode(self.result)

    class Meta:
        db_table = 'timeseriesresults'


class TimeSeriesResultValue(models.Model):
    value_id = models.AutoField(db_column='valueid', primary_key=True)
    result = models.ForeignKey('TimeSeriesResult', db_column='resultid')
    data_value = models.FloatField(db_column='datavalue')
    value_datetime = models.DateTimeField(db_column='valuedatetime')
    value_datetime_utc_offset = models.IntegerField(db_column='valuedatetimeutcoffset')
    censor_code = models.ForeignKey('CensorCode', db_column='censorcodecv')
    quality_code = models.ForeignKey('QualityCode', db_column='qualitycodecv')
    time_aggregation_interval = models.FloatField(db_column='timeaggregationinterval')
    time_aggregation_interval_unit = models.ForeignKey('Unit', db_column='timeaggregationintervalunitsid')

    def __str__(self):
        return str(self.data_value) + ' at ' + str(self.value_datetime) + ' (' + str(self.result) + ')'

    def __unicode__(self):
        return unicode(self.data_value) + ' at ' + unicode(self.value_datetime) + ' (' + unicode(self.result) + ')'

    class Meta:
        db_table = 'timeseriesresultvalues'
