import os


SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(24))

ROOT_URLCONF = 'urls' #


DEBUG = True if 'DEBUG' in os.environ else False
DOMAIN = os.environ.get('DOMAIN', 'localhost')

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ.get('DB_NAME', 'nodeshot'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432')
    },
}

POSTGIS_VERSION = (2, 1)

# import the default nodeshot settings
# do not move this import
from nodeshot.conf.settings import *

# ------ All settings customizations must go here ------ #


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Amsterdam'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

ADMINS = (
    #('Your name', 'your@email.com'),
)

MANAGERS = ADMINS

EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'root@localhost')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER  # used for error reporting

# social auth
FACEBOOK_APP_ID = os.environ.get('FB_APP_ID', '')
FACEBOOK_API_SECRET = os.environ.get('FB_APP_SECRET', '')
GOOGLE_OAUTH2_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
GOOGLE_OAUTH2_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
GITHUB_APP_ID = os.environ.get('GITHUB_APP_ID', '')
GITHUB_API_SECRET = os.environ.get('GITHUB_API_SECRET', '')


try:
    from local_settings import *
except ImportError:
    pass
