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

INSTALLED_APPS.remove('debug_toolbar')

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

#from datetime import timedelta
#
#CELERYBEAT_SCHEDULE = {
#    'synchronize': {
#        'task': 'nodeshot.interop.sync.tasks.synchronize_external_layers',
#        'schedule': timedelta(hours=12),
#    },
#    # example of how to synchronize one of the layers with a different periodicity
#    'synchronize': {
#        'task': 'nodeshot.interop.sync.tasks.synchronize_external_layers',
#        'schedule': timedelta(minutes=30),
#        'args': ('layer_slug',)
#    },
#    # example of how to synchronize all layers except two layers
#    'synchronize': {
#        'task': 'nodeshot.interop.sync.tasks.synchronize_external_layers',
#        'schedule': timedelta(hours=12),
#        'kwargs': { 'exclude': 'layer1-slug,layer2-slug' }
#    }
#}

import django

if django.VERSION[:2] >= (1, 6):
    TEST_RUNNER = 'django.test.runner.DiscoverRunner'
else:
    try:
        import discover_runner
        TEST_RUNNER = "discover_runner.DiscoverRunner"
    except ImportError:
        print("To run tests with django <= 1.5 you should install "
              "django-discover-runner.")
        sys.exit(-1)

try:
    from local_settings import *
except ImportError:
    pass
