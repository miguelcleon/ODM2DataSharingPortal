from datetime import timedelta

import sys
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models.expressions import F

from dataloader.models import TimeSeriesResultValue


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        all_values = TimeSeriesResultValue.objects.only('value_datetime', 'value_datetime_utc_offset')
        print('updating %s data values' % all_values.count())
        counter = 0
        for data_value in all_values:
            data_value.value_datetime = F('value_datetime') - timedelta(hours=data_value.value_datetime_utc_offset)
            data_value.save(update_fields=['value_datetime'])
            counter += 1
            if counter % 1000 == 0:
                print('a thousand data values updated!! only 10 billion left! (%s of them already updated.)' % counter)
        print('all values updated')
