import json
import os

from django.core.management import call_command
from django.test.runner import DiscoverRunner
from django.db import connections

from dataloader.tests.data import data_manager


class ODM2TestRunner(DiscoverRunner):
    test_connection = None
    database_alias = u'odm2'

    def setup_test_environment(self, **kwargs):
        data_manager.load_models_data()
        call_command('makemigrations', 'dataloader')
        super(ODM2TestRunner, self).setup_test_environment(**kwargs)

    def setup_databases(self, **kwargs):
        old_names = []

        self.test_connection = connections[self.database_alias]
        old_names.append((self.test_connection, self.test_connection.settings_dict['NAME'], True))
        self.test_connection.creation.create_test_db(
            verbosity=self.verbosity,
            keepdb=self.keepdb
        )
        return old_names
