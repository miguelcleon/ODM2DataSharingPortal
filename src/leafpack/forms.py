from django import forms
from .models import LeafPack, LeafPackType, Macroinvertebrate, LeafPackBug


class LeafPackForm(forms.ModelForm):

    types = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        queryset=LeafPackType.objects.all(),
        label='Leaf Pack Type and Composition'
    )

    placement_date = forms.DateField()

    class Meta:
        model = LeafPack
        exclude = ['uuid']


class BugCountForm(forms.ModelForm):
    class Meta:
        model = Macroinvertebrate
        fields = ['bug_count']

    def __init__(self, bug, **kwargs):
        super(BugCountForm, self).__init__(**kwargs)

        self.instance = bug
        # Is the macroinvertebrate model instance a Family (in biological classification)?
        self.is_family = bug.family_of is not None
        # Does the model instance have children?
        self.has_children = len(bug.families.all()) > 0

        self.fields['bug_count'].label = self.instance.__str__()

    bug_count = forms.IntegerField(label='Macroinvertebrate', initial=0)


class BugCountFormFactory(forms.BaseFormSet):
    """
    NOTE: The terms 'Order' and 'Family' (or 'Families') in the comments refers to taxonomical biological
    classification.

    BugCountFormFactory.formset_factory() returns a list of tuples, where the element 0 in each tuple is:
        1. An instance of BugCountForm
        2. The model associated with the form is a macroinvertebrate 'Order'
    Element 1 in each tuple is:
        1. A list of BugCountForms
        2. Models associated with the BugCountForms are macroinvertebrates 'Families' of the Order in the first
         element.
        3. Element 1 is an empty list the Order in element 0 has no Families.
    """
    def get_form_kwargs(self, index):
        kwargs = super(BugCountFormFactory, self).get_form_kwargs(index)
        kwargs['instance'] = kwargs['bugs'][index]
        return kwargs

    @staticmethod
    def formset_factory():
        form_list = list()

        # 'Order', as in the biological classification 'Order'
        order_bugs = [bug for bug in Macroinvertebrate.objects.filter(family_of=None).order_by('scientific_name')]

        for order_bug in order_bugs:
            order_bug_form = BugCountForm(order_bug)

            families = order_bug.families.all().order_by('scientific_name')
            family_bug_forms = list()
            if len(families) > 0:
                family_bug_forms = [BugCountForm(bug) for bug in families]

            form_list.append((order_bug_form, family_bug_forms))

        return form_list




