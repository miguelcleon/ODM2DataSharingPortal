from WebSDL.settings.base import *

DEBUG = True

INTERNAL_IPS = (
    '127.0.0.1',
    '129.123.51.198'
)

STATIC_URL = '/static/'
SITE_URL = ''

TEST_RUNNER = 'dataloader.tests.runner.ODM2TestRunner'

EMAIL_HOST = 'mail.usu.edu'

EMAIL_SENDER = data['email_sender'] if 'email_sender' in data else '',
EMAIL_SENDER = EMAIL_SENDER[0] if isinstance(EMAIL_SENDER, tuple) else EMAIL_SENDER
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
