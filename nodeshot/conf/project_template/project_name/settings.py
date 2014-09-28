import os


# ------ BEGIN DON'T TOUCH AREA ------ #

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

SECRET_KEY = '{{ secret_key }}'

ROOT_URLCONF = '{{ project_name }}.urls' #

WSGI_APPLICATION = '{{ project_name }}.wsgi.application'

# ------ END DON'T TOUCH AREA ------ #


DEBUG = True
DOMAIN = '<domain>'
SITE_NAME = '{{ project_name }}'  # site name, you can change this

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'nodeshot',
        'USER': '<user>',
        'PASSWORD':  '<password>',
        'HOST': '127.0.0.1',
        'PORT': '',
    },
    # Import data from older versions
    # More info about this feature here: http://nodeshot.readthedocs.org/en/latest/topics/oldimporter.html
    #'old_nodeshot': {
    #    'ENGINE': 'django.db.backends.mysql',
    #    'NAME': 'nodeshot',
    #    'USER': 'user',
    #    'PASSWORD': 'password',
    #    'OPTIONS': {
    #           "init_command": "SET storage_engine=INNODB",
    #    },
    #    'HOST': '',
    #    'PORT': '',
    #}
}

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

EMAIL_HOST = 'localhost'
EMAIL_HOST_USER = 'root@localhost'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER  # used for error reporting

LEAFLET_CONFIG.update({
    'DEFAULT_CENTER': (49.06775, 30.62011),
    'DEFAULT_ZOOM': 4,
    'MIN_ZOOM': 1,
    'MAX_ZOOM': 18,
    'TILES': 'http://otile1.mqcdn.com/tiles/1.0.0/map/{z}/{x}/{y}.png',
})

# social auth
FACEBOOK_APP_ID = ''
FACEBOOK_API_SECRET = ''
GOOGLE_OAUTH2_CLIENT_ID = ''
GOOGLE_OAUTH2_CLIENT_SECRET = ''
GITHUB_APP_ID = ''
GITHUB_API_SECRET = ''

#from datetime import timedelta
#
#CELERYBEAT_SCHEDULE.update({
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
#})
