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

    def __init__(self, **kwargs):
        kwargs.pop('bugs')  # get rid of 'bugs' keyword before calling super().__init__()
        bug = kwargs.pop('instance')
        super(BugCountForm, self).__init__(**kwargs)
        self.instance = bug
        self.fields['bug_count'].label = self.instance.__str__()

    bug_count = forms.IntegerField(label='Macroinvertebrate', initial=0)


class BaseBugCountFormSet(forms.BaseFormSet):
    def get_form_kwargs(self, index):
        kwargs = super(BaseBugCountFormSet, self).get_form_kwargs(index)
        kwargs['instance'] = kwargs['bugs'][index]
        return kwargs


def bugCountFormSetFactory():
    bugs = [bug for bug in Macroinvertebrate.objects.all()]
    BugCountFormSet = forms.formset_factory(BugCountForm, formset=BaseBugCountFormSet, extra=len(bugs))
    return BugCountFormSet(form_kwargs={'bugs': bugs})


