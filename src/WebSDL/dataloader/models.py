from __future__ import unicode_literals
import uuid

from django.db import models

# TODO: import settings and get dbs, use reflection to add schema name depending on the type of database.


# Controlled Vocabularies

class ControlledVocabulary(models.Model):
    term = models.TextField(db_column='Term')
    name = models.TextField(db_column='Name', primary_key=True)
    definition = models.TextField(db_column='Definition', blank=True)
    category = models.TextField(db_column='Category', blank=True)
    source_vocabulary_uri = models.TextField(db_column='SourceVocabularyURI', blank=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    class Meta:
        managed = False
        abstract = True


class SamplingFeatureType(ControlledVocabulary):
    class Meta:
        db_table = 'CV_SamplingFeatureType'


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


class VariableType(ControlledVocabulary):
    class Meta:
        db_table = 'CV_VariableType'


class VariableName(ControlledVocabulary):
    class Meta:
        db_table = 'CV_VariableName'


# ODM2 Core models

class SamplingFeature(models.Model):
    sampling_feature_id = models.AutoField(db_column='SamplingFeatureID', primary_key=True)
    sampling_feature_type = models.ForeignKey('SamplingFeatureType', db_column='SamplingFeatureTypeCV')
    sampling_feature_code = models.TextField(db_column='SamplingFeatureCode')
    sampling_feature_name = models.TextField(db_column='SamplingFeatureName', blank=True)
    sampling_feature_description = models.TextField(db_column='SamplingFeatureDescription', blank=True)
    elevation_m = models.FloatField(db_column='Elevation_m', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SamplingFeatures'


class FeatureAction(models.Model):
    feature_action_id = models.AutoField(db_column='FeatureActionID', primary_key=True)
    sampling_feature = models.ForeignKey('SamplingFeature', related_name="feature_action", db_column='SamplingFeatureID')
    action = models.ForeignKey('Action', related_name="feature_action", db_column='ActionID')

    class Meta:
        managed = False
        db_table = 'FeatureActions'


class Action(models.Model):
    action_id = models.AutoField(db_column='ActionID', primary_key=True)
    action_type = models.ForeignKey('ActionType', db_column='ActionTypeCV')
    method = models.ForeignKey('Method', db_column='MethodID')
    begin_datetime = models.DateTimeField(db_column='BeginDateTime')
    begin_datetime_utc_offset = models.IntegerField(db_column='BeginDateTimeUTCOffset')
    action_description = models.TextField(db_column='ActionDescription', blank=True)

    class Meta:
        managed = False
        db_table = 'Actions'


class ActionBy(models.Model):
    bridge_id = models.AutoField(db_column='BridgeID', primary_key=True)
    action = models.ForeignKey('Action', related_name="action_by", db_column='ActionID')
    affiliation = models.ForeignKey('Affiliation', db_column='AffiliationID')
    is_action_lead = models.BooleanField(db_column='IsActionLead', default=None)
    role_description = models.TextField(db_column='RoleDescription', blank=True)

    class Meta:
        managed = False
        db_table = 'ActionBy'


class Method(models.Model):
    method_id = models.AutoField(db_column='MethodID', primary_key=True)
    method_type = models.ForeignKey('MethodType', db_column='MethodTypeCV')
    method_code = models.TextField(db_column='MethodCode')
    method_name = models.TextField(db_column='MethodName')
    method_description = models.TextField(db_column='MethodDescription', blank=True)
    method_link = models.TextField(db_column='MethodLink', blank=True)
    organization = models.ForeignKey('Organization', db_column='OrganizationID', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Methods'


class People(models.Model):
    person_id = models.AutoField(db_column='PersonID', primary_key=True)
    person_first_name = models.TextField(db_column='PersonFirstName')
    person_middle_name = models.TextField(db_column='PersonMiddleName', blank=True)
    person_last_name = models.TextField(db_column='PersonLastName')

    class Meta:
        managed = False
        db_table = 'People'


class Organization(models.Model):
    organization_id = models.AutoField(db_column='OrganizationID', primary_key=True)
    organization_type = models.ForeignKey('OrganizationType', db_column='OrganizationTypeCV')
    organization_code = models.TextField(db_column='OrganizationCode')
    organization_name = models.TextField(db_column='OrganizationName')
    organization_description = models.TextField(db_column='OrganizationDescription', blank=True)
    organization_link = models.TextField(db_column='OrganizationLink', blank=True)
    parent_organization = models.ForeignKey('self', db_column='ParentOrganizationID', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Organizations'


class Affiliation(models.Model):
    affiliation_id = models.AutoField(db_column='AffiliationID', primary_key=True)
    person = models.ForeignKey('People', related_name='affiliation', db_column='PersonID')
    organization = models.ForeignKey('Organization', related_name='affiliation', db_column='OrganizationID', blank=True, null=True)
    is_primary_organization_contact = models.NullBooleanField(db_column='IsPrimaryOrganizationContact', default=None)
    affiliation_start_date = models.DateField(db_column='AffiliationStartDate')
    affiliation_end_date = models.DateField(db_column='AffiliationEndDate', blank=True, null=True)
    primary_phone = models.TextField(db_column='PrimaryPhone', blank=True)
    primary_email = models.TextField(db_column='PrimaryEmail')
    primary_address = models.TextField(db_column='PrimaryAddress', blank=True)
    person_link = models.TextField(db_column='PersonLink', blank=True)

    class Meta:
        managed = False
        db_table = 'Affiliations'


class ProcessingLevel(models.Model):
    processing_level_id = models.IntegerField(db_column='ProcessingLevelID', primary_key=True)
    processing_level_code = models.TextField(db_column='ProcessingLevelCode')
    definition = models.TextField(db_column='Definition', blank=True)
    explanation = models.TextField(db_column='Explanation', blank=True)

    class Meta:
        managed = False
        db_table = 'ProcessingLevels'


class Unit(models.Model):
    unit_id = models.IntegerField(db_column='UnitsID', primary_key=True)
    unit_type = models.ForeignKey('UnitType', db_column='UnitsTypeCV')
    unit_abbreviation = models.TextField(db_column='UnitsAbbreviation')
    unit_name = models.TextField(db_column='UnitsName')

    class Meta:
        managed = False
        db_table = 'Units'


class Variable(models.Model):
    variable_id = models.IntegerField(db_column='VariableID', primary_key=True)
    variable_type = models.ForeignKey('VariableType', db_column='VariableTypeCV')
    variable_code = models.TextField(db_column='VariableCode')
    variable_name = models.ForeignKey('VariableName', db_column='VariableNameCV')
    variable_definition = models.TextField(db_column='VariableDefinition', blank=True)
    no_data_value = models.FloatField(db_column='NoDataValue')

    def natural_key(self):
        return self.variablecode + ' ' + self.variabletypecv.name

    class Meta:
        managed = False
        db_table = 'Variables'


class Result(models.Model):
    result_id = models.AutoField(db_column='ResultID', primary_key=True)
    result_uuid = models.TextField(db_column='ResultUUID', default=uuid.uuid4)
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

    class Meta:
        managed = False
        db_table = 'Results'


class SpatialReference(models.Model):
    spatial_reference_id = models.IntegerField(db_column='SpatialReferenceID', primary_key=True)
    srs_code = models.TextField(db_column='SRSCode', blank=True)
    srs_name = models.TextField(db_column='SRSName')
    srs_description = models.TextField(db_column='SRSDescription', blank=True)

    def __str__(self):
        return self.srsname

    def __unicode__(self):
        return self.srsname

    class Meta:
        managed = False
        db_table = 'SpatialReferences'


class TimeSeriesResult(models.Model):
    result_id = models.ForeignKey(Result, db_column='ResultID', primary_key=True)
    x_location = models.FloatField(db_column='XLocation', blank=True, null=True)
    x_location_unit = models.ForeignKey('Unit', related_name='time_series_x_locations', db_column='XLocationUnitsID', blank=True, null=True)
    y_location = models.FloatField(db_column='YLocation', blank=True, null=True)
    y_location_unit = models.ForeignKey('Unit', related_name='time_series_y_locations', db_column='YLocationUnitsID', blank=True, null=True)
    z_location = models.FloatField(db_column='ZLocation', blank=True, null=True)
    z_location_unit = models.ForeignKey('Unit', related_name='time_series_z_locations', db_column='ZLocationUnitsID', blank=True, null=True)
    spatial_reference = models.ForeignKey('SpatialReference', db_column='SpatialReferenceID', blank=True, null=True)
    intended_time_spacing = models.FloatField(db_column='IntendedTimeSpacing', blank=True, null=True)
    intended_time_spacing_unit = models.ForeignKey('Unit', related_name='time_series_intended_time_spacing', db_column='IntendedTimeSpacingUnitsID', blank=True, null=True)
    aggregation_statistic_cv = models.ForeignKey('AggregationStatistic', db_column='AggregationStatisticCV')
