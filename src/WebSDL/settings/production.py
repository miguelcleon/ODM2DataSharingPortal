import django
from WebSDL.settings.base import *

DEBUG = False

ALLOWED_HOSTS = ['localhost', '127.0.0.1', data['host']]

SITE_ROOT = os.environ['APPL_PHYSICAL_PATH']
SITE_URL = os.environ['APPL_VIRTUAL_PATH'] + '/'

STATIC_ROOT = os.path.join(SITE_ROOT, 'static')
STATIC_URL = SITE_URL + 'static/'

EMAIL_HOST = 'mail.usu.edu'

EMAIL_SENDER = data['email_sender'] if 'email_sender' in data else '',
EMAIL_SENDER = EMAIL_SENDER[0] if isinstance(EMAIL_SENDER, tuple) else EMAIL_SENDER
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

django.setup()
