from django.core.management import call_command
from django.test.runner import DiscoverRunner, get_unique_databases_and_mirrors
from django.db import connections
from django.apps import apps


class ODM2TestRunner(DiscoverRunner):
    models = []
    test_connection = None
    database_alias = u'odm2'

    def __init__(self, **kwargs):
        super(ODM2TestRunner, self).__init__(**kwargs)
        self.models = [model for model in apps.get_models() if model._meta.app_label is 'dataloader']

    def setup_test_environment(self, **kwargs):
        for model in self.models:
            model._meta.managed = True
        #call_command('makemigrations', 'dataloader')
        super(ODM2TestRunner, self).setup_test_environment(**kwargs)

    def teardown_test_environment(self, **kwargs):
        super(ODM2TestRunner, self).teardown_test_environment(**kwargs)
        for model in self.models:
            model._meta.managed = False

    def setup_databases(self, **kwargs):
        old_names = []

        self.test_connection = connections[self.database_alias]
        #database_signature = self.test_connection.creation.test_db_signature()
        old_names.append((self.test_connection, self.test_connection.settings_dict['NAME'], True))
        self.test_connection.creation.create_test_db(
            verbosity=self.verbosity,
            keepdb=self.keepdb
        )
        return old_names



    # def teardown_databases(self, old_config, **kwargs):
    #     pass
