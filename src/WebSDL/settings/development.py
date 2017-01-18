from WebSDL.settings.base import *

DEBUG = True

INTERNAL_IPS = (
    '127.0.0.1',
    '129.123.51.198'
)

STATIC_URL = '/static/'
SITE_URL = ''

TEST_RUNNER = 'dataloader.tests.runner.ODM2TestRunner'
