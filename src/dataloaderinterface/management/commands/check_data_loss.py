import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models.aggregates import Max
from django.core.mail import send_mail

from dataloaderinterface.models import SiteRegistration, SiteSensor, SiteAlert


class Command(BaseCommand):
    help = ''

    # imma need to be able to send emails from another method later, let's do the email sending thing here.
    @staticmethod
    def send_email(email_address, subject, message):
        success = send_mail(subject, message, settings.NOTIFY_EMAIL_SENDER, ['fryarludwig@gmail.com'])
        return True if success == 1 else False

    def handle(self, *args, **options):
        ALLOWED_TIME = datetime.timedelta(days=23)
        # get all sites that have alerts, and prefetch all the users who are listening
        sites = SiteRegistration.objects.exclude(alert_listeners__isnull=True) \
            .prefetch_related('alert_listeners', 'sensors') \
            .annotate(latest_measurement=Max('sensors__last_measurement_datetime')) \
            .all()
        for site in sites:  # type: SiteRegistration
            last_update = site.sensors.aggregate(last_update=Max('last_measurement_datetime'))  # type: datetime.datetime
            if last_update is not None and last_update['last_update'] is not None:
                last_update = last_update['last_update']
                time_delta = datetime.datetime.now() - last_update
            else:
                time_delta = datetime.datetime.now() - site.registration_date

            if time_delta > ALLOWED_TIME:
                listeners = site.alert_listeners.all()
                for listener in listeners:
                    last_alert_sent = SiteAlert.objects.filter(site_registration=site.registration_id,
                                                               user=listener.id).all()

                    if last_alert_sent is not None:
                        last_alerted = last_alert_sent.aggregate(last_alerted=Max('last_alerted'))
                        if last_alerted is not None and last_alerted['last_alerted'] is not None:
                            alert_time_delta = datetime.datetime.now() - last_alerted['last_alerted']
                            if alert_time_delta < ALLOWED_TIME:
                                continue

                    time_delta_string = str(time_delta).split(',')[0]
                    subject = 'EnviroDIY Notification: No data received for site' \
                              ' {} in the last {}'.format(site.sampling_feature_name, time_delta_string)

                    message = ("{},\n\n"
                               "This email is to notify you that your EnviroDIY site \"{}\" has not received any new "
                               "data values in the last {}. The last update was on {}. You may want to check your "
                               "equipment to ensure it's working as intended. \n\n"
                               "https://data.envirodiy.org/sites/{}/\n\n"
                               "Best regards,\n"
                               "The data.envirodiy.org team.\n"
                               "").format(listener.first_name, site.sampling_feature_name, time_delta_string,
                                          last_update, site.sampling_feature_code)
                    success = Command.send_email(listener.email, subject, message)
                    site_alert_data = {'user': listener,
                                       'site_registration': site,
                                       'last_alerted': datetime.datetime.now(),
                                       'hours_threshold': 15
                    }

                    site_alert = SiteAlert(**site_alert_data)
                    site_alert.save()

