# -*- coding: utf-8 -*-

import re
from django import forms
from hydroshare.models import HydroShareResource


class MDLRadioButton(forms.RadioSelect):
    def render(self, name, value, attrs=None, renderer=None):
        """Adds MDL HTML classes to label and input tags"""
        html = super(MDLRadioButton, self).render(name, value, attrs=attrs, renderer=renderer)
        html = re.sub(r'</?(ul|li).*?>', '', html)
        html = re.sub(r'(<label )', r'\1class="mdl-radio mdl-js-radio mdl-js-ripple-effect" ', html)
        html = re.sub(r'(<input )', r'\1class="mdl-radio__button" ', html)
        return html


class HydroShareSettingsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(HydroShareSettingsForm, self).__init__(*args, **kwargs)
        # if 'site_registration' in self.initial:
        #     site = self.initial['site_registration']
        # elif len(args) > 0:
        #     site = args[0]['site_registration']
        # self.resources = forms.ModelChoiceField(queryset=HydroShareResource.objects.filter(site_registration=site),
        #                                         required=False)

    schedule_choices = (
        ('scheduled', 'Scheduled'),
        ('manual', 'Manual')
    )
    data_type_choices = (
        ('TS', 'Time Series'),
        ('LP', 'Leaf Packet'),
        ('SD', 'Stream Data')
    )
    schedule_freq_choices = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly')
    )

    pause_sharing = forms.BooleanField(initial=False, label='Pause Sharing', required=False)

    site_registration = forms.CharField(max_length=255)

    schedule_type = forms.ChoiceField(
        widget=MDLRadioButton,
        choices=schedule_choices,
        initial='scheduled'
    )

    update_freq = forms.ChoiceField(
        required=False,
        widget=forms.Select,
        choices=schedule_freq_choices,
        initial='daily'
    )

    data_types = forms.MultipleChoiceField(
        # TODO: When EnviroDIY supports multiple data types, the 'required' attribute should be set to True
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=data_type_choices,
        initial='TS',
        error_messages={'required': 'Please select at least one data type.'}
    )

    abstract = forms.CharField(
        required=False,
        widget=forms.Textarea,
        label='Abstract'
    )

    title = forms.CharField(
        required=False,
        widget=forms.TextInput,
        label='Resource Title',
    )

    resources = forms.ModelChoiceField(queryset=HydroShareResource.objects.all(), required=False)

    # TODO: Make this a model form
    # class Meta:
    #     model = HydroShareResource
    #     fields = ['hs_account', 'ext_id', 'site_registration', 'sync_type', 'update_freq', 'is_enabled', 'data_types']


class HydroShareResourceDeleteForm(forms.Form):
    delete_external_resource = forms.BooleanField(
        initial=False,
        label="Delete connected resource in HydroShare.",
        required=False)
