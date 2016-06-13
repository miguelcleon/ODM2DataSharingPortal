from __future__ import unicode_literals
import uuid

from django.db import models

# TODO: import settings and get dbs, use reflection to add schema name depending on the type of database.


# Controlled Vocabularies

class ControlledVocabulary(models.Model):
    term = models.CharField(db_column='Term', max_length=255)
    name = models.CharField(db_column='Name', primary_key=True, max_length=255)
    definition = models.CharField(db_column='Definition', blank=True, max_length=500)
    category = models.CharField(db_column='Category', blank=True, max_length=255)
    source_vocabulary_uri = models.CharField(db_column='SourceVocabularyURI', blank=True, max_length=255)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True


class SamplingFeatureType(ControlledVocabulary):
    class Meta:
        db_table = 'CV_SamplingFeatureType'


class ElevationDatum(ControlledVocabulary):
    class Meta:
        db_table = 'CV_ElevationDatum'


class ActionType(ControlledVocabulary):
    class Meta:
        db_table = 'CV_ActionType'


class MethodType(ControlledVocabulary):
    class Meta:
        db_table = 'CV_MethodType'


class OrganizationType(ControlledVocabulary):
    class Meta:
        db_table = 'CV_OrganizationType'


class ResultType(ControlledVocabulary):
    class Meta:
        db_table = 'CV_ResultType'


class Medium(ControlledVocabulary):
    class Meta:
        db_table = 'CV_Medium'


class AggregationStatistic(ControlledVocabulary):
    class Meta:
        db_table = 'CV_AggregationStatistic'


class CensorCode(ControlledVocabulary):
    class Meta:
        db_table = 'CV_CensorCode'


class Status(ControlledVocabulary):
    class Meta:
        db_table = 'CV_Status'


class UnitType(ControlledVocabulary):
    class Meta:
        db_table = 'CV_UnitType'


class QualityCode(ControlledVocabulary):
    class Meta:
        db_table = 'QualityCodeCV'


class VariableType(ControlledVocabulary):
    class Meta:
        db_table = 'CV_VariableType'


class VariableName(ControlledVocabulary):
    class Meta:
        db_table = 'CV_VariableName'


# ODM2 Core models

class SamplingFeature(models.Model):
    sampling_feature_id = models.AutoField(db_column='SamplingFeatureID', primary_key=True)
    sampling_feature_uuid = models.UUIDField(default=uuid.uuid4, editable=False, db_column='SamplingFeatureUUID')
    sampling_feature_type = models.ForeignKey('SamplingFeatureType', db_column='SamplingFeatureTypeCV')
    sampling_feature_code = models.CharField(db_column='SamplingFeatureCode', max_length=50)
    sampling_feature_name = models.CharField(db_column='SamplingFeatureName', blank=True, max_length=255)
    sampling_feature_description = models.CharField(db_column='SamplingFeatureDescription', blank=True, max_length=500)
    elevation_m = models.FloatField(db_column='Elevation_m', blank=True, null=True)
    elevation_datum = models.ForeignKey('ElevationDatum', db_column='ElevationDatumCV', blank=True, null=True)

    def __str__(self):
        return str(self.sampling_feature_type_id) + ': ' + self.sampling_feature_code + ' ' + self.sampling_feature_name

    def __unicode__(self):
        return unicode(self.sampling_feature_type_id) + ': ' + self.sampling_feature_code + ' ' + self.sampling_feature_name

    class Meta:
        db_table = 'SamplingFeatures'


class FeatureAction(models.Model):
    feature_action_id = models.AutoField(db_column='FeatureActionID', primary_key=True)
    sampling_feature = models.ForeignKey('SamplingFeature', related_name="feature_action", db_column='SamplingFeatureID')
    action = models.ForeignKey('Action', related_name="feature_action", db_column='ActionID')

    def __str__(self):
        return str(self.action) + ' ' + self.sampling_feature.sampling_feature_code + ' (' + str(self.sampling_feature.sampling_feature_type) + ')'

    def __unicode__(self):
        return unicode(self.action) + ' ' + self.sampling_feature.sampling_feature_code + ' (' + unicode(self.sampling_feature.sampling_feature_type) + ')'

    class Meta:
        db_table = 'FeatureActions'


class Action(models.Model):
    action_id = models.AutoField(db_column='ActionID', primary_key=True)
    action_type = models.ForeignKey('ActionType', db_column='ActionTypeCV')
    method = models.ForeignKey('Method', db_column='MethodID')
    begin_datetime = models.DateTimeField(db_column='BeginDateTime')
    begin_datetime_utc_offset = models.IntegerField(db_column='BeginDateTimeUTCOffset')
    action_description = models.TextField(db_column='ActionDescription', blank=True)

    def __str__(self):
        return str(self.action_type_id) + ' - ' + str(self.begin_datetime) + ' ' + str(self.begin_datetime_utc_offset)

    def __unicode__(self):
        return unicode(self.action_type_id) + ' - ' + unicode(self.begin_datetime) + ' ' + unicode(self.begin_datetime_utc_offset)

    class Meta:
        db_table = 'Actions'


class ActionBy(models.Model):
    bridge_id = models.AutoField(db_column='BridgeID', primary_key=True)
    action = models.ForeignKey('Action', related_name="action_by", db_column='ActionID')
    affiliation = models.ForeignKey('Affiliation', db_column='AffiliationID')
    is_action_lead = models.BooleanField(db_column='IsActionLead', default=None)
    role_description = models.CharField(db_column='RoleDescription', blank=True, max_length=255)

    def __str__(self):
        return str(self.action) + ': ' + str(self.affiliation)

    def __unicode__(self):
        return unicode(self.action) + ': ' + unicode(self.affiliation)

    class Meta:
        db_table = 'ActionBy'


class Method(models.Model):
    method_id = models.AutoField(db_column='MethodID', primary_key=True)
    method_type = models.ForeignKey('MethodType', db_column='MethodTypeCV')
    method_code = models.CharField(db_column='MethodCode', max_length=50)
    method_name = models.CharField(db_column='MethodName', max_length=255)
    method_description = models.CharField(db_column='MethodDescription', blank=True, max_length=500)
    method_link = models.CharField(db_column='MethodLink', blank=True, max_length=255)
    organization = models.ForeignKey('Organization', db_column='OrganizationID', blank=True, null=True)

    def __str__(self):
        return str(self.method_type_id) + ': ' + self.method_name

    def __unicode__(self):
        return unicode(self.method_type_id) + ': ' + self.method_name

    class Meta:
        db_table = 'Methods'


class People(models.Model):
    person_id = models.AutoField(db_column='PersonID', primary_key=True)
    person_first_name = models.CharField(db_column='PersonFirstName', max_length=255)
    person_middle_name = models.CharField(db_column='PersonMiddleName', blank=True, max_length=255)
    person_last_name = models.CharField(db_column='PersonLastName', max_length=255)

    def __str__(self):
        return self.person_first_name + ' ' + self.person_last_name

    def __unicode__(self):
        return self.person_first_name + ' ' + self.person_last_name

    class Meta:
        db_table = 'People'


class Organization(models.Model):
    organization_id = models.AutoField(db_column='OrganizationID', primary_key=True)
    organization_type = models.ForeignKey('OrganizationType', db_column='OrganizationTypeCV')
    organization_code = models.CharField(db_column='OrganizationCode', max_length=50)
    organization_name = models.CharField(db_column='OrganizationName', max_length=255)
    organization_description = models.CharField(db_column='OrganizationDescription', blank=True, max_length=500)
    organization_link = models.CharField(db_column='OrganizationLink', blank=True, max_length=255)
    parent_organization = models.ForeignKey('self', db_column='ParentOrganizationID', blank=True, null=True)

    def __str__(self):
        return str(self.organization_type_id) + ': ' + self.organization_name

    def __unicode__(self):
        return unicode(self.organization_type_id) + ': ' + self.organization_name

    class Meta:
        db_table = 'Organizations'


class Affiliation(models.Model):
    affiliation_id = models.AutoField(db_column='AffiliationID', primary_key=True)
    person = models.ForeignKey('People', related_name='affiliation', db_column='PersonID')
    organization = models.ForeignKey('Organization', related_name='affiliation', db_column='OrganizationID', blank=True, null=True)
    is_primary_organization_contact = models.NullBooleanField(db_column='IsPrimaryOrganizationContact', default=None)
    affiliation_start_date = models.DateField(db_column='AffiliationStartDate')
    affiliation_end_date = models.DateField(db_column='AffiliationEndDate', blank=True, null=True)
    primary_phone = models.CharField(db_column='PrimaryPhone', blank=True, max_length=50)
    primary_email = models.CharField(db_column='PrimaryEmail', max_length=255)
    primary_address = models.CharField(db_column='PrimaryAddress', blank=True, max_length=255)
    person_link = models.CharField(db_column='PersonLink', blank=True, max_length=255)

    def __str__(self):
        return str(self.person) + ' (' + self.organization.organization_name + ') - ' + self.primary_email

    def __unicode__(self):
        return unicode(self.person) + ' (' + self.organization.organization_name + ') - ' + self.primary_email

    class Meta:
        db_table = 'Affiliations'


class ProcessingLevel(models.Model):
    processing_level_id = models.AutoField(db_column='ProcessingLevelID', primary_key=True)
    processing_level_code = models.CharField(db_column='ProcessingLevelCode', max_length=50)
    definition = models.CharField(db_column='Definition', blank=True, max_length=500)
    explanation = models.CharField(db_column='Explanation', blank=True, max_length=500)

    def __str__(self):
        return self.processing_level_code + ' (' + self.definition + ')'

    def __unicode__(self):
        return self.processing_level_code + ' (' + self.definition + ')'

    class Meta:
        db_table = 'ProcessingLevels'


class Unit(models.Model):
    unit_id = models.AutoField(db_column='UnitsID', primary_key=True)
    unit_type = models.ForeignKey('UnitType', db_column='UnitsTypeCV')
    unit_abbreviation = models.CharField(db_column='UnitsAbbreviation', max_length=255)
    unit_name = models.CharField(db_column='UnitsName', max_length=255)

    def __str__(self):
        return str(self.unit_type_id) + ': ' + self.unit_abbreviation + ' (' + self.unit_name + ')'

    def __unicode__(self):
        return unicode(self.unit_type_id) + ': ' + self.unit_abbreviation + ' (' + self.unit_name + ')'

    class Meta:
        db_table = 'Units'


class Variable(models.Model):
    variable_id = models.AutoField(db_column='VariableID', primary_key=True)
    variable_type = models.ForeignKey('VariableType', db_column='VariableTypeCV')
    variable_code = models.CharField(db_column='VariableCode', max_length=50)
    variable_name = models.ForeignKey('VariableName', db_column='VariableNameCV')
    variable_definition = models.CharField(db_column='VariableDefinition', blank=True, max_length=255)
    no_data_value = models.FloatField(db_column='NoDataValue')

    def __str__(self):
        return str(self.variable_name) + ': ' + self.variable_code + ' (' + str(self.variable_type_id) + ')'

    def __unicode__(self):
        return unicode(self.variable_name) + ': ' + self.variable_code + ' (' + unicode(self.variable_type_id) + ')'

    class Meta:
        db_table = 'Variables'


class Result(models.Model):
    result_id = models.AutoField(db_column='ResultID', primary_key=True)
    result_uuid = models.CharField(db_column='ResultUUID', default=uuid.uuid4, max_length=255)
    feature_action = models.ForeignKey('FeatureAction', db_column='FeatureActionID')
    result_type = models.ForeignKey('ResultType', db_column='ResultTypeCV')
    variable = models.ForeignKey('Variable', db_column='VariableID')
    unit = models.ForeignKey('Unit', db_column='UnitsID')
    processing_level = models.ForeignKey(ProcessingLevel, db_column='ProcessingLevelID')
    result_datetime = models.DateTimeField(db_column='ResultDateTime', blank=True, null=True)
    result_datetime_utc_offset = models.BigIntegerField(db_column='ResultDateTimeUTCOffset', blank=True, null=True)
    status = models.ForeignKey('Status', db_column='StatusCV', blank=True)
    sampled_medium = models.ForeignKey('Medium', db_column='SampledMediumCV')
    value_count = models.IntegerField(db_column='ValueCount')

    def __str__(self):
        return str(self.result_datetime) + ' - ' + str(self.result_type_id) + ' (' + str(self.variable.variable_name_id) + '): ' + self.variable.variable_code + ' ' + self.unit.unit_abbreviation

    def __unicode__(self):
        return unicode(self.result_datetime) + ' - ' + unicode(self.result_type_id) + ' (' + unicode(self.variable.variable_name_id) + '): ' + self.variable.variable_code + ' ' + self.unit.unit_abbreviation

    class Meta:
        db_table = 'Results'


class TimeSeriesResult(models.Model):
    result = models.OneToOneField(Result, db_column='ResultID', primary_key=True)
    x_location = models.FloatField(db_column='XLocation', blank=True, null=True)
    x_location_unit = models.ForeignKey('Unit', related_name='time_series_x_locations', db_column='XLocationUnitsID', blank=True, null=True)
    y_location = models.FloatField(db_column='YLocation', blank=True, null=True)
    y_location_unit = models.ForeignKey('Unit', related_name='time_series_y_locations', db_column='YLocationUnitsID', blank=True, null=True)
    z_location = models.FloatField(db_column='ZLocation', blank=True, null=True)
    z_location_unit = models.ForeignKey('Unit', related_name='time_series_z_locations', db_column='ZLocationUnitsID', blank=True, null=True)
    intended_time_spacing = models.FloatField(db_column='IntendedTimeSpacing', blank=True, null=True)
    intended_time_spacing_unit = models.ForeignKey('Unit', related_name='time_series_intended_time_spacing', db_column='IntendedTimeSpacingUnitsID', blank=True, null=True)
    aggregation_statistic_cv = models.ForeignKey('AggregationStatistic', db_column='AggregationStatisticCV')

    def __str__(self):
        return str(self.result)

    def __unicode__(self):
        return unicode(self.result)

    class Meta:
        db_table = 'TimeSeriesResults'


class TimeSeriesResultValue(models.Model):
    value_id = models.AutoField(db_column='ValueID', primary_key=True)
    result = models.ForeignKey('TimeSeriesResult', db_column='ResultID')
    data_value = models.FloatField(db_column='DataValue')
    value_datetime = models.DateTimeField(db_column='ValueDateTime')
    value_datetime_utc_offset = models.IntegerField(db_column='ValueDateTimeUTCOffset')
    censor_code = models.ForeignKey('CensorCode', db_column='CensorCodeCV')
    quality_code = models.ForeignKey('QualityCode', db_column='QualityCodeCV')
    time_aggregation_interval = models.FloatField(db_column='TimeAggregationInterval')
    time_aggregation_interval_unit = models.ForeignKey('Unit', db_column='TimeAggregationIntervalUnitsID')

    def __str__(self):
        return str(self.data_value) + ' at ' + str(self.value_datetime) + ' (' + str(self.result) + ')'

    def __unicode__(self):
        return unicode(self.data_value) + ' at ' + unicode(self.value_datetime) + ' (' + unicode(self.result) + ')'

    class Meta:
        db_table = 'TimeSeriesResultValues'
