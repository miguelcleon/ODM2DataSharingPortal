from __future__ import unicode_literals

from django.apps import AppConfig
import crontab_jobs
from django.utils.termcolors import colorize

class DataloaderinterfaceConfig(AppConfig):
    name = 'dataloaderinterface'

    # def ready(self):
    #     user = True
    #     scheduledJobs.start_jobs(user=user)
