from django import forms
from .models import LeafPack, LeafPackType, Macroinvertebrate, LeafPackBug
from dataloaderinterface.models import SiteRegistration
from django.utils.safestring import mark_safe


class MDLCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, renderer=None):
        html = '<ul id="id_' + name + '" class="mdl-list list-leafpack-types row">'
        for choice in self.choices:
            field_id = "id_" + name + "_" + str(choice[0])
            field_value = str(choice[0])
            is_checked = "checked" if isinstance(choice, list) and choice[0] in value else ""
            label = str(choice[1])
            html += '<li class="mdl-list__item col-sm-6 col-lg-4">' \
                    '<span class="mdl-list__item-primary-content">' \
                    '</span>' \
                    '<span class="mdl-list__item-secondary-action">' \
                    '<label class="mdl-checkbox mdl-js-checkbox mdl-js-ripple-effect vertical-align-center" for="' + field_id + '">' \
                    '<input type="checkbox" id="' + field_id + '" name="' + name + '"' \
                    ' class="mdl-checkbox__input" ' + is_checked + ' value="' + field_value + '" />' \
                    + label + \
                    '</label>' \
                    '</span>' \
                    '</li>'
        html += '</ul>'
        html = mark_safe(html)
        return html


class LeafPackForm(forms.ModelForm):
    site_registration = forms.ModelChoiceField(
        widget=forms.HiddenInput,
        queryset=SiteRegistration.objects.all()
    )

    types = forms.ModelMultipleChoiceField(
        widget=MDLCheckboxSelectMultiple,
        queryset=LeafPackType.objects.all(),
    )

    placement_date = forms.DateField(
        label='Placement Date'
    )

    leafpack_placement_count = forms.IntegerField(
        label='Number of Packs Placed',
        min_value=0
    )

    placement_air_temp = forms.FloatField(
        label='Placement Air Temperature'
    )

    placement_water_temp = forms.FloatField(
        label='Placement Water Temperature'
    )

    retrieval_date = forms.DateField(
        label='Retrieval Date'
    )

    leafpack_retrieval_count = forms.IntegerField(
        label='Number of Packs Retrieved',
        min_value=0
    )

    retrieval_air_temp = forms.FloatField(
        label='Retrieval Air Temperature'
    )

    retrieval_water_temp = forms.FloatField(
        label='Retrieval Water Temperature'
    )

    had_storm = forms.BooleanField(
        widget=forms.NullBooleanSelect,
        label='Did storms occur while your leaf packs were in the stream?',
        required=False
    )

    storm_count = forms.IntegerField(
        label='Number of storms that occurred',
        min_value=0,
        required=False
    )

    storm_precipitation = forms.FloatField(
        label='Total precipitation that occurred',
        min_value=0,
        required=False
    )

    had_flood = forms.BooleanField(
        widget=forms.NullBooleanSelect,
        label='Did flooding occur?',
        required=False
    )

    had_drought = forms.BooleanField(
        widget=forms.NullBooleanSelect,
        label='Was this site experiencing a drought during your experiment?',
        required=False
    )

    class Meta:
        model = LeafPack
        exclude = ['uuid', 'bugs']


class LeafPackBugForm(forms.ModelForm):
    class Meta:
        model = LeafPackBug
        fields = ['bug_count']

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs and kwargs['instance'].bug:
            kwargs['prefix'] = kwargs['instance'].bug.scientific_name

        super(LeafPackBugForm, self).__init__(*args, **kwargs)

        if self.instance and getattr(self.instance, 'bug', None):
            # Is the macroinvertebrate model instance a Family (in biological classification)?
            self.is_family = self.instance.bug.family_of is not None
            # Does the model instance have children?
            self.has_children = len(self.instance.bug.families.all()) > 0

            self.fields['bug_count'].label = self.instance.bug.common_name + ' (' + self.instance.bug.scientific_name + ')'


class LeafPackBugFormFactory(forms.BaseFormSet):
    """
    NOTE: The terms 'Order' and 'Family' (or 'Families') in the comments refers to taxonomical biological
    classification.

    LeafPackBugFormFactory.formset_factory() returns a list of tuples, where the element 0 in each tuple is:
        1. An instance of LeafPackBugForm
        2. The model associated with the form is a macroinvertebrate 'Order'
    Element 1 in each tuple is:
        1. A list of BugCountForms
        2. Models associated with the BugCountForms are macroinvertebrates 'Families' of the Order in the first
         element.
        3. Element 1 is an empty list the Order in element 0 has no Families.
    """
    def get_form_kwargs(self, index):
        kwargs = super(LeafPackBugFormFactory, self).get_form_kwargs(index)
        kwargs['instance'] = kwargs['bugs'][index]
        return kwargs

    @staticmethod
    def formset_factory(leafpack=None):
        form_list = []

        order_bugs = [bug for bug in Macroinvertebrate.objects.filter(family_of=None).order_by('common_name')]

        for order_bug in order_bugs:
            if leafpack is not None:
                lpg = LeafPackBug.objects.get(bug=order_bug.id, leaf_pack=leafpack.id)
            else:
                lpg = LeafPackBug(bug=order_bug)

            order_bug_form = LeafPackBugForm(instance=lpg)

            families = order_bug.families.all().order_by('scientific_name')
            family_bug_forms = list()
            if len(families) > 0:
                family_bug_forms = [LeafPackBugForm(instance=LeafPackBug(bug=bug)) for bug in families]

            form_list.append((order_bug_form, family_bug_forms))

        return form_list

