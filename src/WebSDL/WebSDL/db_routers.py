import sys


class WebSDLRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'dataloader':
            return 'odm2'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label in ['dataloader', 'dataloaderservices']:
            return 'odm2'
        return 'default'

    def allow_migrate(self, db, app_label, **hints):
        allow = app_label not in ['dataloader', 'dataloaderservices'] or 'test' in sys.argv
        return allow
