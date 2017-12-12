from django.core.management.base import BaseCommand
from django.db.models.aggregates import Max

from dataloaderinterface.models import SiteRegistration


class Command(BaseCommand):
    help = ''

    # imma need to be able to send emails from another method later, let's do the email sending thing here.
    @staticmethod
    def send_email():
        pass

    def handle(self, *args, **options):
        # get all sites that have alerts, and prefetch all the users who are listening
        sites = SiteRegistration.objects\
            .exclude(alert_listeners__isnull=True)\
            .prefetch_related('alert_listeners', 'sensors') \
            .annotate(latest_measurement=Max('sensors__last_measurement_datetime'))\
            .all()
        for site in sites:
            # TODO: yeayeayea
            continue
