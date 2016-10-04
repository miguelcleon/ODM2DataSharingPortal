from dal import autocomplete
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms.formsets import formset_factory
from djangoformsetjs.utils import formset_media_js

from dataloader.models import SamplingFeature, Action, People, Organization, Affiliation, Result, ActionBy, Method, \
    OrganizationType, Site


# AUTHORIZATION
class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(required=True, max_length=50)
    last_name = forms.CharField(required=True, max_length=50)

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


# ODM2
class SamplingFeatureForm(forms.ModelForm):
    class Meta:
        model = SamplingFeature
        fields = [
            'sampling_feature_code',
            'sampling_feature_name',
            'elevation_m',
            'elevation_datum',
        ]
        labels = {
            'sampling_feature_code': 'Site Code',
            'sampling_feature_name': 'Site Name',
            'elevation_m': 'Elevation',
        }


class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = [
            'site_type',
            'latitude',
            'longitude',
        ]


class ActionForm(forms.ModelForm):
    class Meta:
        model = Action
        fields = [
            'method',
        ]
        labels = {
            'method': 'Method'
        }


class ActionByForm(forms.ModelForm):
    class Meta:
        model = ActionBy
        fields = [
            'affiliation',
        ]
        labels = {
            'affiliation': 'Action Lead'
        }


class PeopleForm(forms.ModelForm):
    class Meta:
        model = People
        fields = [
            'person_first_name',
            'person_last_name',
        ]
        labels = {
            'person_first_name': 'First Name',
            'person_last_name': 'Last Name',
        }


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = [
            'organization_code',
            'organization_name',
        ]


class AffiliationForm(forms.ModelForm):
    class Meta:
        model = Affiliation
        fields = [
            'primary_phone',
            'primary_email',
            'primary_address',
            'affiliation_start_date',
        ]
        labels = {
            'affiliation_start_date': 'Affiliation Date',
            'primary_phone': 'Phone',
            'primary_email': 'Email',
            'primary_address': 'Address',
        }


class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = [
            'variable',
            'unit',
            'sampled_medium',
            'processing_level',
        ]


ResultFormSet = formset_factory(ResultForm, extra=0, can_order=False, min_num=1, validate_min=True)
