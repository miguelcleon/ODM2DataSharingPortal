from datetime import timedelta

import sys
from django.core.management.base import BaseCommand
from django.db import transaction

from dataloader.models import TimeSeriesResultValue


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        all_values = TimeSeriesResultValue.objects.only('value_datetime', 'value_datetime_utc_offset')
        print('updating %s data values' % all_values.count())
        for data_value in all_values:
            sys.stdout.write('.')
            data_value.value_datetime = data_value.value_datetime - timedelta(hours=data_value.value_datetime_utc_offset)
            data_value.save(update_fields=['value_datetime'])
        print('all values updated')
