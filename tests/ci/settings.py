import os


# ------ BEGIN DON'T TOUCH AREA ------ #

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

SECRET_KEY = '+fxm7u#!*+%=-+#g@tqp5^^gg0jp#dh37^6#0j7v_plcvjk1ro'

ROOT_URLCONF = 'ci.urls' #

WSGI_APPLICATION = 'ci.wsgi.application'

# ------ END DON'T TOUCH AREA ------ #


DEBUG = True
DOMAIN = 'localhost'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'nodeshot_ci',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },
    # Import data from older versions
    # More info about this feature here: http://nodeshot.readthedocs.org/en/latest/topics/oldimporter.html
    'old_nodeshot': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'nodeshot_old_ci',
        'USER': 'root',
        'PASSWORD': '',
        'OPTIONS': {
               "init_command": "SET storage_engine=INNODB",
        },
        'HOST': '',
        'PORT': '',
    }
}

POSTGIS_VERSION = (2, 1)

# import the default nodeshot settings
# do not move this import
from nodeshot.conf.settings import *

# ------ All settings customizations must go here ------ #

TIME_ZONE = 'Europe/Amsterdam'
LANGUAGE_CODE = 'en-gb'
ADMINS = ()
MANAGERS = ADMINS

EMAIL_HOST = 'localhost'
EMAIL_HOST_USER = 'root@localhost'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER  # used for error reporting

# social auth
SOCIAL_AUTH_FACEBOOK_KEY = ''
SOCIAL_AUTH_FACEBOOK_SECRET = ''
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = ''
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = ''
SOCIAL_AUTH_GITHUB_KEY = ''
SOCIAL_AUTH_GITHUB_SECRET = ''


try:
    from local_settings import *
except ImportError:
    pass
