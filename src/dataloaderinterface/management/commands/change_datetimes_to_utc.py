from datetime import timedelta

import sys
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models.expressions import F, ExpressionWrapper
from django.db.models.fields import DateTimeField

from dataloader.models import TimeSeriesResultValue


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        for offset in range(-7, 1):
            print('Getting data values with utc offset %s' % offset)
            all_values = TimeSeriesResultValue.objects.filter(value_datetime_utc_offset=offset)
            print('updating values...')
            all_values.update(value_datetime=(F('value_datetime') - timedelta(hours=offset)))
            print('values updated')
        print('ALL values updated')
