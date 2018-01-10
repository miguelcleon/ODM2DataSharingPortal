from dataloader.models import SamplingFeature, Result
from django import template
from django.core.exceptions import ObjectDoesNotExist

from dataloaderinterface.csv_serializer import SiteResultSerializer
from dataloaderinterface.models import DeviceRegistration, SiteSensor, SiteRegistration

register = template.Library()
#
#
# @register.filter(name='get_registration')
# def get_registration(sampling_feature):
#     if not isinstance(sampling_feature, SamplingFeature):
#         return
#
#     return DeviceRegistration.objects.filter(deployment_sampling_feature_uuid__exact=sampling_feature.sampling_feature_uuid).first()


@register.filter(name='get_sensor_csv_path')
def get_sensor_csv_path(sensor):
    if not isinstance(sensor, SiteSensor):
        return
    try:
        return SiteResultSerializer(sensor.result).get_file_path()
    except ObjectDoesNotExist:
        return None


@register.filter(name='get_site_sensor')
def get_site_sensor(site, variable_code):
    if not isinstance(site, SiteRegistration):
        return

    return site.sensors.filter(variable_code=variable_code).first()


@register.filter(name='can_administer_site')
def can_administer_site():
    pass
    # return DeviceRegistration.objects.filter(deployment_sampling_feature_uuid__exact=sampling_feature.sampling_feature_uuid).first()
