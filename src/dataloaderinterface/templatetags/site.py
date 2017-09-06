from dataloader.models import SamplingFeature, Result
from django import template

from dataloaderinterface.csv_serializer import SiteResultSerializer
from dataloaderinterface.models import DeviceRegistration, SiteSensor

register = template.Library()


@register.filter(name='get_registration')
def get_registration(sampling_feature):
    if not isinstance(sampling_feature, SamplingFeature):
        return

    return DeviceRegistration.objects.filter(deployment_sampling_feature_uuid__exact=sampling_feature.sampling_feature_uuid).first()


@register.filter(name='get_sensor_csv_path')
def get_sensor_csv_path(sensor):
    if not isinstance(sensor, SiteSensor):
        return

    return SiteResultSerializer(sensor.result).get_file_path()


@register.filter(name='can_administer_site')
def can_administer_site():
    pass
    # return DeviceRegistration.objects.filter(deployment_sampling_feature_uuid__exact=sampling_feature.sampling_feature_uuid).first()
