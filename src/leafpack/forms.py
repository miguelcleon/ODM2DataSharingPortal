from django import forms
from .models import LeafPack, LeafPackType, Macroinvertebrate, LeafPackBug
from dataloaderinterface.models import SiteRegistration


class LeafPackForm(forms.ModelForm):

    site_registration = forms.ModelChoiceField(
        widget=forms.HiddenInput,
        queryset=SiteRegistration.objects.all()
    )

    types = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        queryset=LeafPackType.objects.all(),
        label='Leaf Pack Type and Composition'
    )

    placement_date = forms.DateField(
        label='Placement Date'
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

            self.fields['bug_count'].label = self.instance.bug.common_name


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




