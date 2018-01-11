from django.core.management.base import BaseCommand
from django.db.models.aggregates import Count, Min

from dataloader.models import Result
from dataloaderinterface.models import SiteRegistration


class Command(BaseCommand):
    help = ''

    def update_sensors_activation_date(self, site):
        for sensor in site.sensors.all():
            series_result = sensor.result.timeseriesresult
            if series_result.values.count() == 0:
                continue

            earliest_value = series_result.values.earliest('value_datetime')
            sensor.activation_date = earliest_value.value_datetime
            sensor.activation_date_utc_offset = earliest_value.value_datetime_utc_offset
            sensor.save(update_fields=['activation_date', 'activation_date_utc_offset'])

    def handle(self, *args, **options):
        sites = SiteRegistration.objects.prefetch_related('sensors').all()
        for site in sites:
            self.update_sensors_activation_date(site)
            min_datetime = site.sensors.aggregate(first_light=Min('activation_date'))
            site.deployment_date = min_datetime['first_light']
            site.save(update_fields=['deployment_date'])