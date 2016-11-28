from datetime import datetime

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.db.models.query_utils import Q
from django.forms.formsets import formset_factory

from dataloaderinterface.models import ODM2User
from dataloader.models import SamplingFeature, Action, People, Organization, Affiliation, Result, ActionBy, Method, \
    Site, EquipmentModel, Medium

# AUTHORIZATION


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(required=True, max_length=50)
    last_name = forms.CharField(required=True, max_length=50)
    organization = forms.ModelChoiceField(queryset=Organization.objects.all(), required=False)

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        organization = self.cleaned_data['organization']

        if commit:
            person = People.objects.filter(person_first_name=user.first_name, person_last_name=user.last_name).first() or \
                People.objects.create(person_first_name=user.first_name, person_last_name=user.last_name)
            affiliation = Affiliation.objects.filter(person=person, organization=organization).first() or \
                Affiliation.objects.create(person=person, organization=organization, affiliation_start_date=datetime.now())

            user.save()
            ODM2User.objects.create(user=user, affiliation_id=affiliation.affiliation_id)

        return user


# ODM2
class SamplingFeatureForm(forms.ModelForm):
    use_required_attribute = False

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
    use_required_attribute = False

    class Meta:
        model = Site
        fields = [
            'site_type',
            'latitude',
            'longitude',
        ]


class ActionForm(forms.ModelForm):
    use_required_attribute = False
    method = forms.ModelChoiceField(label='Method', queryset=Method.objects.filter(method_type__name='Instrument deployment'))

    class Meta:
        model = Action
        fields = [
            'method',
        ]


class ActionByForm(forms.ModelForm):
    use_required_attribute = False

    class Meta:
        model = ActionBy
        fields = [
            'affiliation',
        ]
        labels = {
            'affiliation': 'Action Lead'
        }


class PeopleForm(forms.ModelForm):
    use_required_attribute = False

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
    use_required_attribute = False

    class Meta:
        model = Organization
        fields = [
            'organization_code',
            'organization_name',
            'organization_type'
        ]


class AffiliationForm(forms.ModelForm):
    use_required_attribute = False

    class Meta:
        model = Affiliation
        fields = [
            'primary_phone',
            'primary_email',
            'affiliation_start_date',
        ]
        labels = {
            'affiliation_start_date': 'Affiliation Date',
            'primary_phone': 'Phone',
            'primary_email': 'Email',
        }


class ResultForm(forms.ModelForm):
    use_required_attribute = False

    def __init__(self, *args, **kwargs):
        super(ResultForm, self).__init__(*args, **kwargs)
        self.empty_permitted = False

    equipment_model = forms.ModelChoiceField(queryset=EquipmentModel.objects.all())
    sampled_medium = forms.ModelChoiceField(queryset=Medium.objects.filter(Q(pk='Air') | Q(pk='Liquid aqueous')))

    class Meta:
        model = Result
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


ResultFormSet = formset_factory(ResultForm, extra=0, can_order=False, min_num=1, validate_min=True)
