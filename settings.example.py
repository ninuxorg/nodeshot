# Django settings for nodeshot project.

import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('admin', 'admin@yourdomain.org'),
)

ORGANIZATION = 'Ninux.org'

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'nodeshot.db',               # Or path to database file if using sqlite3.
        'USER': 'nodeshot',                     # Not used with sqlite3.
        'PASSWORD': 'XXXXX',             # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        # if using mysql we suggest to use INNODB as storage engine
        #'OPTIONS': {
        #    'init_command': 'SET storage_engine=INNODB',
        #}
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
LANGUAGE_CODE = 'en-EN'

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

# for django 1.4
STATIC_ROOT = '%s/static/' % os.path.dirname(os.path.realpath(__file__))

SITE_URL = "http://localhost:8000/"

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '%smedia/' % SITE_URL

# for django 1.4
STATIC_URL = '%sstatic/' % SITE_URL

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
# DEPRECATED
#ADMIN_MEDIA_PREFIX = '%sadmin/' % MEDIA_URL

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
    # staticgenerator
    #'staticgenerator.middleware.StaticGeneratorMiddleware'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    # nodeshot
    'nodeshot.context_processors.site'
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
    #'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'rosetta',
    'nodeshot',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

# additional information about administrators
AUTH_PROFILE_MODULE = 'nodeshot.UserProfile'

# If you use the django development server set this to true if you want django to serve static files (check urls.py)
DEVELOPMENT_SERVER = True

# google map center for nodeshot
NODESHOT_GMAP_CONFIG = {
    'lat': '41.8934',
    'lng': '12.4960',
    'zoom': 12
}

# site name and domain, this is needed for email notifications We wanted to avoid using Django's sites framework
NODESHOT_SITE = {
    'name': 'Nodeshot',
    'domain': 'domain.com'
}

# this setting is used in the generation of KML file
NODESHOT_KML = {
    'name': NODESHOT_SITE['name'],
    'description': 'KML feed generated by Nodeshot.'
}

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
# maximum number of days to activate a new node until is purged (automatic purging needs a cronjob to be set on the server)
NODESHOT_ACTIVATION_DAYS = 7
# log messages sent with contact form
NODESHOT_LOG_CONTACTS = False

_ = lambda s: s

NODESHOT_FRONTEND_SETTINGS = {
    'HTML_TITLE_INDEX': 'Nodeshot, Open Source Map Server',
    'META_ROBOTS': 'noindex,nofollow',
    'SHOW_STATISTICS': True,
    'SHOW_KML_LINK': True,
    'HELP_URL': 'http://wiki.ninux.org/UsareMapserver',
    'SHOW_ADMIN_LINK': True,
    'TAB3': 'OLSR',
    'TAB4': 'VPN',
    'WELCOME_TEXT': _('Welcome to Nodeshot!'),
    'LINK_QUALITY': 'etx' # nometric, dbm, etx
}

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'youremail@gmail.com'
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = 'youremail@gmail.com'

# captcha settings
MATH_CAPTCHA_NUMBERS = range(1,9)
MATH_CAPTCHA_OPERATORS = '+'
MATH_CAPTCHA_QUESTION = _('Antispam question: what is the sum of')

# static generator
# to activate static generator follow instructions here http://superjared.com/projects/static-generator/
WEB_ROOT = '/var/www/nodeshot/' # you need to change this with your public folder
STATIC_GENERATOR_URLS = (
    r'^/$',
    r'^/overview/$',
    r'^/select',
    r'^/nodes.json$',
    r'^/jstree.json$',
    r'^/search',
    r'^/node/info',
    r'^/node/advanced',
    r'^/tab',
    r'^/nodes.kml$',
)

# Settings for the read_topology_hna.py script
# to retrieve topologies from remote islands
TOPOLOGY_URL_TIMEOUT=30
ETX_THRESHOLD=23.0
OLSR_URLS=["http://127.0.0.1:2006/all"]
BATMAN_URLS=[]

#rosetta config
ROSETTA_EXCLUDED_APPLICATIONS = ('rosetta',)
ROSETTA_MESSAGES_PER_PAGE = 20
