from django.core.management.base import BaseCommand
from django.db.models.aggregates import Count
from django.db.models.query_utils import Q

from dataloader.models import Result, Medium


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
        equipment_medium_variables = ['Battery voltage', '']
        equipment_medium = Medium.objects.filter(pk='Equipment').first()
        if not equipment_medium:
            equipment_medium = Medium.objects.create(**equipment_medium)

        # TODO: change board temp and battery voltage under load when you know what those actually are.
        # Result.objects.prefetch_related('variable').filter(variable__variable_name_id__in=['Battery voltage', ])
