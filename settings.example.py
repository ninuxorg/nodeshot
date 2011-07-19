# Django settings for nodeshot project.

import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('admin', 'admin@yourdomain.org'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'nodeshot',                      # Or path to database file if using sqlite3.
        'USER': 'nodeshot',                      # Not used with sqlite3.
        'PASSWORD': 'XXXXX',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Rome'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'it-IT'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '%s/media/' % os.path.dirname(os.path.realpath(__file__))

# If you use the django development server set this to true if you want django to serve static files (check urls.py)
DEVELOPMENT_SERVER = True

if DEVELOPMENT_SERVER:
	SITE_URL = "http://localhost:8000/"
else:
	SITE_URL = "http://nodeshot.peertoport.com/"

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '%smedia/' % SITE_URL

# for django 1.4
STATIC_URL = MEDIA_URL

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '%sadmin/' % MEDIA_URL

# Make this unique, and don't share it with anybody.
SECRET_KEY = '(i+!)&s9crw*eg^!)(uudsdr%+*+g)(d$fs32eh7a3*z-dd3'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '%s/nodeshot/templates/' % os.path.dirname(os.path.realpath(__file__))
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'nodeshot',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

# site name, will be used in emails
SITE_NAME = 'Nodeshot'

# routing protocols used in nodeshot.models
NODESHOT_ROUTING_PROTOCOLS = (
    ('aodv','AODV'),
    ('batman','B.A.T.M.A.N.'),
    ('dsdv','DSDV'),
    ('dsr','DSR'),
    ('hsls','HSLS'),
    ('iwmp','IWMP'),
    ('olsr','OLSR'),
    ('oorp','OORP'),
    ('ospf','OSPF'),
    ('tora','TORA'),
)
# set your default routing protocol
NODESHOT_DEFAULT_ROUTING_PROTOCOL = 'olsr'
NODESHOT_ACTIVATION_DAYS = 7

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'youremail@gmail.com'
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = 'youremail@gmail.com'