from __future__ import unicode_literals
import subprocess

from django.apps import AppConfig
import scheduledJobs


class DataloaderinterfaceConfig(AppConfig):
    name = 'dataloaderinterface'

    def ready(self):
        scheduledJobs.start_jobs(user=True)
