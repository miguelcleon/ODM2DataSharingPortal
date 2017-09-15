from django.core.management.base import BaseCommand
from django.db.models.aggregates import Count
from django.db.models.query_utils import Q

from dataloader.models import Result, Medium
from dataloaderinterface.models import SiteSensor


class Command(BaseCommand):
    help = ''

    def get_medium_data(self):
        equipment_data = {
            'term': 'equipment',
            'name': 'Equipment',
            'definition': 'An instrument, sensor or other piece of human-made equipment upon which a measurement is made,'
                          ' such as datalogger temperature or battery voltage.',
        }
        return equipment_data

    def handle(self, *args, **options):
        equipment_medium_variables = ['EnviroDIY_Mayfly_Temp', 'EnviroDIY_Mayfly_Volt', 'EnviroDIY_Mayfly_FreeSRAM']
        equipment_medium = Medium.objects.filter(pk='Equipment').first()
        if not equipment_medium:
            equipment_medium = Medium.objects.create(**self.get_medium_data())

        results = Result.objects.prefetch_related('variable').filter(variable__variable_code__in=equipment_medium_variables)
        sensors = SiteSensor.objects.filter(variable_code__in=equipment_medium_variables)
        results.update(sampled_medium=equipment_medium)
        sensors.update(sampled_medium=equipment_medium.name)
