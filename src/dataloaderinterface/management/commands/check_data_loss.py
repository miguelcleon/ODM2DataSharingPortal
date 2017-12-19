import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models.aggregates import Max
from django.core.mail import send_mail

from dataloaderinterface.models import SiteRegistration, SiteSensor, SiteAlert


class Command(BaseCommand):
    help = ''

    @staticmethod
    def send_email(email_address, subject, message):
        success = send_mail(subject, message, settings.NOTIFY_EMAIL_SENDER, [email_address])
        return True if success == 1 else False

    def handle(self, *args, **options):
        # TODO: juan: this is not complete. needs subquery magic to get the timedelta between now and last measurement taking into account the utc offset.
        all_alert_sites = SiteAlert.objects\
            .prefetch_related('site_registration__sensors', 'user')\
            .annotate(site_last_measurement=Max('site_registration__sensors__last_measurement_datetime'))\
            .filter(site_last_measurement__isnull=False)\
            .all()

        for site_alert in all_alert_sites:
            # last_update = site_alert.site_registration.sensors.aggregate(last_update=Max('last_measurement_datetime'))['last_update']
            # if last_update is None:
            #     # print 'No data values have ever been received'
            #     continue
            time_delta = datetime.datetime.now() - site_alert.site_last_measurement
            if time_delta < datetime.timedelta(hours=site_alert.hours_threshold):
                # print 'Still within the time delta'
                continue

            if site_alert.last_alerted is not None:
                if site_alert.last_alerted > site_alert.site_last_measurement:
                    continue  # We've already emailed them for this issue, let's not spam them

            time_delta_string = str(time_delta).split(',')[0]

            subject = 'EnviroDIY Notification: No data received for site' \
                      ' {} in the last {}'.format(site_alert.site_registration.sampling_feature_name, time_delta_string)

            message = ("{},\n\n"
                       "This email is to notify you that your EnviroDIY site \"{}\" has not received any new "
                       "data values in the last {}. The last update was on {}. You may want to check your "
                       "equipment to ensure it's working as intended. \n\n"
                       "https://data.envirodiy.org/sites/{}/\n\n"
                       "Best regards,\n"
                       "The data.envirodiy.org team.\n"
                       "").format(site_alert.user.first_name, site_alert.site_registration.sampling_feature_name,
                                  time_delta_string, site_alert.site_last_measurement,
                                  site_alert.site_registration.sampling_feature_code)
            success = Command.send_email(site_alert.user.email, subject, message)
            if success:
                site_alert.last_alerted = datetime.datetime.now()
                site_alert.save()
            else:
                # TODO: kene: what if the email failed?
                continue
