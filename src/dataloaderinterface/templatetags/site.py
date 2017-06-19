from dataloader.models import SamplingFeature
from django import template

from dataloaderinterface.models import DeviceRegistration

register = template.Library()


@register.filter(name='get_registration')
def get_registration(sampling_feature):
    if not isinstance(sampling_feature, SamplingFeature):
        return

    return DeviceRegistration.objects.filter(deployment_sampling_feature_uuid__exact=sampling_feature.sampling_feature_uuid).first()
