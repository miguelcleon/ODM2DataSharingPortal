from datetime import datetime

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db.models.query_utils import Q
from django.forms.formsets import formset_factory

from dataloaderinterface.models import ODM2User
from dataloader.models import SamplingFeature, Action, People, Organization, Affiliation, Result, ActionBy, Method, \
    Site, EquipmentModel, Medium, OrganizationType, DataLoggerProgramFile


# AUTHORIZATION


class UserRegistrationForm(UserCreationForm):
    use_required_attribute = False

    first_name = forms.CharField(required=True, max_length=50)
    last_name = forms.CharField(required=True, max_length=50)
    email = forms.EmailField(required=True, max_length=254)
    organization = forms.ModelChoiceField(queryset=Organization.objects.all().exclude(organization_type__in=['Vendor', 'Manufacturer']), required=False, help_text='Choose your affiliated organization')

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        organization = self.cleaned_data['organization']

        if commit:
            user.save()
            person = People.objects.create(person_first_name=user.first_name, person_last_name=user.last_name)
            affiliation = Affiliation.objects.create(person=person, organization=organization, affiliation_start_date=datetime.now(), primary_email=user.email)
            ODM2User.objects.create(user=user, affiliation_id=affiliation.affiliation_id)

        return user


# ODM2

class OrganizationForm(forms.ModelForm):
    use_required_attribute = False
    organization_type = forms.ModelChoiceField(queryset=OrganizationType.objects.all().exclude(name__in=['Vendor', 'Manufacturer']), required=False, help_text='Choose the type of organization')

    class Meta:
        model = Organization
        help_texts = {
            'organization_code': 'Enter an organization code',
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
    use_required_attribute = False

    class Meta:
        model = Site
        help_texts = {
            'site_type': 'Select the type of site you are deploying (e.g., "Stream")',
            'latitude': 'Enter the latitude of your site in decimal degrees (e.g., 40.6893)',
            'longitude': 'Enter the longitude of your site in decimal degrees (e.g., -75.2033)',
        }
        fields = [
            'site_type',
            'latitude',
            'longitude',
        ]


class ResultForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ResultForm, self).__init__(*args, **kwargs)
        self.empty_permitted = False

    equipment_model = forms.ModelChoiceField(queryset=EquipmentModel.objects.all(), help_text='Choose the model of your sensor')
    sampled_medium = forms.ModelChoiceField(queryset=Medium.objects.filter(
        Q(pk='Air') |
        Q(pk='Soil') |
        Q(pk='Liquid aqueous')
    ), help_text='Choose the sampled medium')

    class Meta:
        model = Result
        help_texts = {
            'equipment_model': 'Choose the model of your sensor',
            'variable': 'Choose the measured variable',
            'unit': 'Choose the measured units',
            'sampled_medium': 'Choose the sampled medium'
        }
        fields = [
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


ResultFormSet = formset_factory(ResultForm, extra=0, can_order=False, min_num=0)
