# -*- coding: utf-8 -*-

from django.forms import NumberInput
from django.forms.widgets import HiddenInput

from dataloader.models import SamplingFeature, Organization, Affiliation, Result, Site, EquipmentModel, Medium, \
    OrganizationType, ActionBy, SiteType, Variable, Unit
from django import forms
from django.forms.formsets import formset_factory
import re

from dataloaderinterface.models import SiteRegistration, SiteAlert, SiteSensor, SensorOutput
from hydroshare.models import HydroShareResource

allowed_site_types = [
    'Borehole', 'Ditch', 'Atmosphere', 'Estuary', 'House', 'Land', 'Pavement', 'Stream', 'Spring',
    'Lake, Reservoir, Impoundment', 'Laboratory or sample-preparation area', 'Observation well', 'Soil hole',
    'Storm sewer', 'Stream gage', 'Tidal stream', 'Water quality station', 'Weather station', 'Wetland', 'Other'
]


class SiteTypeSelect(forms.Select):
    site_types = {
        name: definition
        for (name, definition)
        in SiteType.objects.filter(name__in=allowed_site_types).values_list('name', 'definition')
    }

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super(SiteTypeSelect, self).create_option(name, value, label, selected, index, subindex, attrs)
        option['attrs']['title'] = self.site_types[value] if value in self.site_types else ''
        return option


class SampledMediumField(forms.ModelChoiceField):
    custom_labels = {
        'Liquid aqueous': 'Water - Liquid Aqueous'
    }

    @staticmethod
    def get_custom_label(medium):
        return SampledMediumField.custom_labels[medium] if medium in SampledMediumField.custom_labels else medium

    def label_from_instance(self, obj):
        return SampledMediumField.get_custom_label(obj.name)


# ODM2

class SiteRegistrationForm(forms.ModelForm):
    affiliation_id = forms.ModelChoiceField(
        queryset=Affiliation.objects.for_display(),
        required=False,
        help_text='Select the user that deployed or manages the site',
        label='Deployed By'
    )
    site_type = forms.ModelChoiceField(
        queryset=SiteType.objects.filter(name__in=allowed_site_types),
        help_text='Select the type of site you are deploying (e.g., "Stream")',
        widget=SiteTypeSelect
    )

    def clean_affiliation_id(self):
        return self.data['affiliation_id'] if 'affiliation_id' in self.data else None

    def clean_site_type(self):
        return self.data['site_type']

    class Meta:
        model = SiteRegistration
        fields = [
            'affiliation_id', 'sampling_feature_code', 'sampling_feature_name', 'latitude', 'longitude', 'elevation_m',
            'elevation_datum', 'site_type', 'stream_name', 'major_watershed', 'sub_basin', 'closest_town'
        ]
        labels = {
            'sampling_feature_code': 'Site Code',
            'sampling_feature_name': 'Site Name',
            'elevation_m': 'Elevation',
        }
        help_texts = {
            'sampling_feature_code': 'Enter a brief and unique text string to identify your site (e.g., "Del_Phil")',
            'sampling_feature_name': 'Enter a brief but descriptive name for your site (e.g., "Delaware River near Phillipsburg")',
            'latitude': 'Enter the latitude of your site in decimal degrees (e.g., 40.6893)',
            'longitude': 'Enter the longitude of your site in decimal degrees (e.g., -75.2033)',
            'elevation_m': 'Enter the elevation of your site in meters',
            'elevation_datum': 'Choose the elevation datum for your site\'s elevation. If you don\'t know it, choose "MSL"',
        }


class ActionByForm(forms.ModelForm):
    use_required_attribute = False
    affiliation = forms.ModelChoiceField(queryset=Affiliation.objects.all(), required=False, help_text='Select the user that deployed or manages the site', label='Deployed By')

    class Meta:
        model = ActionBy
        fields = ['affiliation']


class OrganizationForm(forms.ModelForm):
    use_required_attribute = False
    organization_type = forms.ModelChoiceField(queryset=OrganizationType.objects.all().exclude(name__in=['Vendor', 'Manufacturer']), required=False, help_text='Choose the type of organization')

    class Meta:
        model = Organization
        help_texts = {
            'organization_code': 'Enter a brief, but unique code to identify your organization (e.g., "USU" or "USGS")',
            'organization_name': 'Enter the name of your organization',
            'organization_description': 'Enter a description for your organization'
        }
        fields = [
            'organization_code',
            'organization_name',
            'organization_type',
            'organization_description'
        ]


class SamplingFeatureForm(forms.ModelForm):
    use_required_attribute = False
    sampling_feature_name = forms.CharField(required=True, label='Site Name', help_text='Enter a brief but descriptive name for your site (e.g., "Delaware River near Phillipsburg")')

    class Meta:
        model = SamplingFeature
        help_texts = {
            'sampling_feature_code': 'Enter a brief and unique text string to identify your site (e.g., "Del_Phil")',
            'elevation_m': 'Enter the elevation of your site in meters',
            'elevation_datum': 'Choose the elevation datum for your site\'s elevation. If you don\'t know it, choose "MSL"'
        }
        fields = [
            'sampling_feature_code',
            'sampling_feature_name',
            'elevation_m',
            'elevation_datum',
        ]
        labels = {
            'sampling_feature_code': 'Site Code',
            'elevation_m': 'Elevation',
        }


class SiteForm(forms.ModelForm):
    allowed_site_types = [
        'Borehole', 'Ditch', 'Atmosphere', 'Estuary', 'House', 'Land', 'Pavement', 'Stream', 'Spring',
        'Lake, Reservoir, Impoundment', 'Laboratory or sample-preparation area', 'Observation well', 'Soil hole',
        'Storm sewer', 'Stream gage', 'Tidal stream', 'Water quality station', 'Weather station', 'Wetland', 'Other'
    ]

    site_type = forms.ModelChoiceField(
        queryset=SiteType.objects.filter(name__in=allowed_site_types),
        help_text='Select the type of site you are deploying (e.g., "Stream")',
        widget=SiteTypeSelect
    )
    use_required_attribute = False

    class Meta:
        model = Site
        help_texts = {
            'site_type': '',
            'latitude': 'Enter the latitude of your site in decimal degrees (e.g., 40.6893)',
            'longitude': 'Enter the longitude of your site in decimal degrees (e.g., -75.2033)',
        }
        fields = [
            'site_type',
            'latitude',
            'longitude',
        ]


class SiteSensorForm(forms.ModelForm):
    allowed_sampled_medium = ['Air', 'Soil', 'Sediment', 'Liquid aqueous', 'Equipment', 'Not applicable', 'Other']

    id = forms.CharField(widget=HiddenInput(), required=False)
    registration = forms.CharField(widget=HiddenInput())
    output_variable = forms.CharField(widget=HiddenInput())
    result_id = forms.CharField(widget=HiddenInput(), required=False)
    result_uuid = forms.CharField(widget=HiddenInput(), required=False)

    sensor_manufacturer = forms.ModelChoiceField(queryset=Organization.objects.only_vendors(), label='Sensor Manufacturer', help_text='Choose the manufacturer', to_field_name='organization_code')
    sensor_model = forms.ModelChoiceField(queryset=EquipmentModel.objects.all(), label='Sensor Model', help_text='Choose the model of your sensor')
    variable = forms.ModelChoiceField(queryset=Variable.objects.all(), label='Measured Variable', help_text='Choose the measured variable')
    unit = forms.ModelChoiceField(queryset=Unit.objects.all(), label='Units', help_text='Choose the measured units')
    sampled_medium = SampledMediumField(queryset=Medium.objects.filter(pk__in=allowed_sampled_medium), label='Sampled Medium', help_text='Choose the sampled medium')

    def clean_registration(self):
        data = self.data['registration']
        if not data:
            raise forms.ValidationError(message='Site Registration id is required.')
        try:
            instance = SiteRegistration.objects.get(pk=data)
        except SiteRegistration.DoesNotExist:
            raise forms.ValidationError(message='Site Registration not found.')
        return instance

    def clean_output_variable(self):
        data = self.data['output_variable']
        if not data:
            raise forms.ValidationError(message='Output variable id is required.')
        try:
            instance = SensorOutput.objects.get(pk=data)
        except SensorOutput.DoesNotExist:
            raise forms.ValidationError(message='Output variable not found.')
        return instance

    class Meta:
        model = SiteSensor
        fields = [
            'output_variable', 'sensor_manufacturer', 'sensor_model', 'variable', 'unit', 'sampled_medium'
        ]


class ResultForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ResultForm, self).__init__(*args, **kwargs)
        self.empty_permitted = False

    equipment_model = forms.ModelChoiceField(queryset=EquipmentModel.objects.for_display(), help_text='Choose the model of your sensor')
    sampled_medium = SampledMediumField(queryset=Medium.objects.filter(pk__in=[
        'Air', 'Soil', 'Sediment', 'Liquid aqueous',
        'Equipment', 'Not applicable', 'Other'
    ]), help_text='Choose the sampled medium')

    class Meta:
        model = Result
        help_texts = {
            'equipment_model': 'Choose the model of your sensor',
            'variable': 'Choose the measured variable',
            'unit': 'Choose the measured units',
            'sampled_medium': 'Choose the sampled medium'
        }
        fields = [
            'result_id',
            'equipment_model',
            'variable',
            'unit',
            'sampled_medium',
        ]
        labels = {
            'equipment_model': 'Sensor Model',
            'variable': 'Measured Variable',
            'sampled_medium': 'Sampled Medium',
        }


ResultFormSet = formset_factory(ResultForm, extra=0, can_order=False, min_num=1, can_delete=True)


class SiteAlertForm(forms.ModelForm):
    notify = forms.BooleanField(required=False, initial=False, label='Notify me if site stops receiving sensor data.')
    hours_threshold = forms.DurationField(required=False, label='Notify after', widget=NumberInput(attrs={'min': 1}))
    suffix = ' hours of site inactivity.'

    class Meta:
        model = SiteAlert
        fields = ['notify', 'hours_threshold']
        labels = {
            'notify': 'Receive email notifications for this site',
        }

