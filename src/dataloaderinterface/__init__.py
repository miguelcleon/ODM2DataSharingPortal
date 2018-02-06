import sys
import signal
import crontab_jobs

default_app_config = 'dataloaderinterface.apps.DataloaderinterfaceConfig'


def on_dataloaderinterface_shutdown(*args):
    from django.conf import settings
    crontab_jobs.stop_jobs(user=settings.CRONTAB_USER)
    sys.exit(0)


signal.signal(signal.SIGINT, on_dataloaderinterface_shutdown)
signal.signal(signal.SIGTERM, on_dataloaderinterface_shutdown)
