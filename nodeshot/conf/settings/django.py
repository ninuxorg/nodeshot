from __future__ import absolute_import
import os
from django.conf import settings

DEBUG = True
SERVE_STATIC = DEBUG
TEMPLATE_DEBUG = DEBUG

USE_I18N = True

USE_L10N = True

USE_TZ = True

SITE_ID = 1

PROTOCOL = 'http' if DEBUG else 'https'
PORT = '8000' if DEBUG else None
SITE_URL = '%s://%s' % (PROTOCOL, settings.DOMAIN)

if PORT and PORT not in ['80', '443']:
    SITE_URL = '%s:%s' % (SITE_URL, PORT)

MEDIA_ROOT = '%s/media/' % settings.SITE_ROOT

MEDIA_URL = '%s/media/' % SITE_URL

STATIC_ROOT = '%s/static/' % settings.SITE_ROOT

STATIC_URL = '%s/static/' % SITE_URL

ALLOWED_HOSTS = ['*']

if PROTOCOL == 'https':
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    os.environ['HTTPS'] = 'on'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
)


TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.request",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages"
)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    # hstore support
    'django_hstore',
    # admin site
    'grappelli.dashboard',
    'grappelli',
    'filebrowser',
    'django.contrib.admin',
    # celery django email backend
    'djcelery_email',
    # nodeshot
    'nodeshot.core.api',
    'nodeshot.core.layers',
    'nodeshot.core.nodes',
    'nodeshot.core.cms',
    'nodeshot.core.websockets',
    'nodeshot.interoperability',
    'nodeshot.community.participation',
    'nodeshot.community.notifications',
    'nodeshot.community.profiles',
    'nodeshot.community.emailconfirmation',
    'nodeshot.community.mailing',
    'nodeshot.networking.net',
    'nodeshot.networking.links',
    'nodeshot.networking.services',
    'nodeshot.networking.hardware',
    'nodeshot.networking.connectors',
    'nodeshot.ui.default',
    'nodeshot.open311',
    'nodeshot.ui.open311_demo',
    # 3d parthy django apps
    'rest_framework',
    'rest_framework_swagger',
    'olwidget',
    'south',
    'smuggler',
    'reversion',
    'corsheaders',
    'social_auth',
    # other utilities
    'django_extensions',
    'debug_toolbar',
]

AUTH_USER_MODEL = 'profiles.Profile'

if 'old_nodeshot' in settings.DATABASES:
    INSTALLED_APPS.append('nodeshot.extra.oldimporter')
    DATABASE_ROUTERS = [
        'nodeshot.extra.oldimporter.db.DefaultRouter',
        'nodeshot.extra.oldimporter.db.OldNodeshotRouter'
    ]

# ------ DJANGO CACHE ------ #

if DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'redis_cache.cache.RedisCache',
            'LOCATION': '127.0.0.1:6379:1',
            'OPTIONS': {
                'CLIENT_CLASS': 'redis_cache.client.DefaultClient',
            }
        }
    }

    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'

# ------ EMAIL SETTINGS ------ #

EMAIL_HOST_USER = ''
EMAIL_PORT = 1025 if DEBUG else 25  # 1025 if you are in development mode, while 25 is usually the production port
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER  # used for error reporting

# ------ LOGGING ------ #

# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'logfile': {
            'level': 'ERROR',
            'class':'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': settings.SITE_ROOT + "/../log/nodeshot.error.log",
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 3,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers':['logfile'],
            'level':'ERROR',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins', 'logfile'],
            'level': 'ERROR',
            'propagate': True,
        },
        '': {
            'handlers': ['logfile'],
            'level': 'ERROR',
        },
    },
    'formatters': {
        'verbose': {
            'format': '\n\n[%(levelname)s %(asctime)s] module: %(module)s, process: %(process)d, thread: %(thread)d\n%(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'custom': {
            'format': '%(levelname)s %(asctime)s\n%(message)s'
        },
    },
}
