from django import forms
from .models import LeafPack, LeafPackType, Macroinvertebrate, LeafPackBug
from dataloaderinterface.models import SiteRegistration
from django.core.exceptions import ObjectDoesNotExist


class MDLCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    template_name = 'mdl-checkbox-select-multiple.html'

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        context['choices'] = [choice[1][0] for choice in context['widget']['optgroups']]
        context['name'] = name
        return self._render(self.template_name, context, renderer)


class LeafPackForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(LeafPackForm, self).__init__(*args, **kwargs)
        if self.instance is not None and self.instance.pk is not None:
            other_types = self.instance.types.all().filter(created_by__isnull=False)
            self.initial['types_other'] = ', '.join([other.name for other in other_types])

    def save(self, commit=True):
        super(LeafPackForm, self).save(commit=commit)

        # LeafPackTypes from the cleaned form data (these types may or may not exist)
        types_other_cleaned = self.cleaned_data.get('types_other', '').split(',')

        for other in types_other_cleaned:
            # remove leading/trailing white space
            other = other.strip()

            try:
                lptype = LeafPackType.objects.get(name=other)
                self.instance.types.add(lptype)
            except ObjectDoesNotExist:
                continue

        self.instance.save()

    site_registration = forms.ModelChoiceField(
        widget=forms.HiddenInput,
        queryset=SiteRegistration.objects.all()
    )

    types = forms.ModelMultipleChoiceField(
        widget=MDLCheckboxSelectMultiple,
        queryset=LeafPackType.objects.filter(created_by=None),
    )

    types_other = forms.CharField(
        max_length=255,
        label='Enter the three predominant leaf species:',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'i.e: one, two, three'})
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
        exclude = ['bugs']


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
            self.fields['bug_count'].min_value = 0


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

        queryset = Macroinvertebrate.objects.filter(family_of=None)\
            .order_by('pollution_tolerance')\
            .order_by('-sort_priority')

        for taxon in queryset:
            if leafpack is not None:
                lpg = LeafPackBug.objects.get(bug=taxon.id, leaf_pack=leafpack.id)
            else:
                lpg = LeafPackBug(bug=taxon)

            order_bug_form = LeafPackBugForm(instance=lpg)

            families = taxon.families.all().order_by('common_name')
            family_bug_forms = list()
            if len(families) > 0:
                if leafpack is not None:
                    child_taxons = [LeafPackBug.objects.get(bug=bug, leaf_pack=leafpack) for bug in families]
                    family_bug_forms = [LeafPackBugForm(instance=taxon) for taxon in child_taxons]
                else:
                    family_bug_forms = [LeafPackBugForm(instance=LeafPackBug(bug=bug)) for bug in families]

            form_list.append((order_bug_form, family_bug_forms))

        return form_list

