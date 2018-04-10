from django import template

from dataloaderinterface.forms import SampledMediumField

register = template.Library()


@register.filter(name='get_field_data')
def get_field_data(form, field_name):
    display_value = str(form[field_name].field.to_python(form[field_name].data) or form[field_name].initial)
    if field_name == 'sampled_medium':
        display_value = SampledMediumField.get_custom_label(display_value)

    return display_value


@register.filter(name='has_data')
def has_data(form):
    return len(form.changed_data) or len(form.initial)


@register.filter(name='is_deleted')
def is_deleted(form):
    return 'DELETE' in form.changed_data
