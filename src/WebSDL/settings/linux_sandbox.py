from WebSDL.settings.base import *

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
if "host" in data:
    ALLOWED_HOSTS.append(data["host"])
if "host_alt" in data:
    ALLOWED_HOSTS.append(data["host_alt"])
if "host_staging" in data:
    ALLOWED_HOSTS.append(data["host_staging"])

if "hydroshare_oauth" in data:
    os.environ.setdefault("HS_CLIENT_ID", data["hydroshare_oauth"]["client_id"])
    os.environ.setdefault("HS_CLIENT_SECRET", data["hydroshare_oauth"]["client_secret"])
    os.environ.setdefault("HS_REDIRECT_URI", data["hydroshare_oauth"]["redirect_uri"])
    os.environ.setdefault("HS_RESPONSE_TYPE", data["hydroshare_oauth"]["response_type"])

STATIC_ROOT = data["static_root"]
SITE_ROOT = "/opt/websdlenvironment/"
STATIC_URL = '/static/'
SITE_URL = ''