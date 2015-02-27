import os
import sys
from datetime import timedelta
from django.conf import settings

DEBUG = settings.DEBUG
SERVE_STATIC = DEBUG
TEMPLATE_DEBUG = DEBUG

USE_I18N = True

USE_L10N = True

USE_TZ = True

PROTOCOL = 'http' if DEBUG else 'https'
PORT = getattr(settings, 'PORT', '8000') if DEBUG else None

if PORT and str(PORT) not in ['80', '443']:
    PORT_STRING = ':%s' % PORT
else:
    PORT_STRING = ''

SUBDIR = getattr(settings, 'SUBDIR', '')

if SUBDIR and not SUBDIR.startswith('/'):
    SUBDIR = '/%s' % SUBDIR
elif SUBDIR and SUBDIR.endswith('/'):
    SUBDIR = SUBDIR[0:-1]

SITE_URL = '%s://%s%s%s' % (PROTOCOL, settings.DOMAIN, PORT_STRING, SUBDIR)
SITE_NAME = getattr(settings, 'SITE_NAME', 'Nodeshot')

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
    'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',  # sentry
    'raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware',  # sentry
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
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    # hstore support
    'django_hstore',
    # celery django email backend
    'djcelery_email',
    # nodeshot
    'nodeshot.core.api',
    'nodeshot.core.layers',
    'nodeshot.core.nodes',
    'nodeshot.core.cms',
    'nodeshot.core.websockets',
    'nodeshot.interop.sync',
    'nodeshot.ui.default',
    'nodeshot.community.participation',
    'nodeshot.community.notifications',
    'nodeshot.community.profiles',
    'nodeshot.community.mailing',
    'nodeshot.networking.net',
    'nodeshot.networking.links',
    'nodeshot.networking.services',
    'nodeshot.networking.hardware',
    'nodeshot.networking.connectors',
    'nodeshot.interop.open311',
    'nodeshot.ui.open311_demo',
    # admin site
    'grappelli.dashboard',
    'grappelli',
    'filebrowser',
    'django.contrib.admin',
    # 3d parthy django apps
    'rest_framework',
    'rest_framework_swagger',
    'leaflet',
    'south',
    'smuggler',
    'reversion',
    'corsheaders',
    'social_auth',
    'rosetta',
    # other utilities
    'django_extensions',
    'debug_toolbar',
]

AUTH_USER_MODEL = 'profiles.Profile'

if getattr(settings, 'RAVEN_CONFIG', {}):
    INSTALLED_APPS.append('raven.contrib.django.raven_compat')

if 'old_nodeshot' in settings.DATABASES:
    INSTALLED_APPS.append('nodeshot.interop.oldimporter')
    DATABASE_ROUTERS = [
        'nodeshot.interop.oldimporter.db.DefaultRouter',
        'nodeshot.interop.oldimporter.db.OldNodeshotRouter'
    ]

# ------ FILEBROWSER ------ #

FILEBROWSER_DIRECTORY = ''

# ------ DJANGO CACHE ------ #

CACHES = {
    'rosetta': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'rosetta'
    }
}

if DEBUG:
    CACHES['default'] = {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
else:
    CACHES['default'] = {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': '127.0.0.1:6379:1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }

    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'

# ------ EMAIL SETTINGS ------ #

EMAIL_PORT = 1025 if DEBUG else 25  # 1025 if you are in development mode, while 25 is usually the production port

# ------ LOGGING ------ #

# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '\n\n[%(levelname)s %(asctime)s] module: %(module)s, process: %(process)d, thread: %(thread)d\n%(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'logfile': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': settings.SITE_ROOT + "/../log/nodeshot.error.log",
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 3,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['logfile'],
            'level': 'ERROR',
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
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        }
    }
}

# ------ CELERY ------ #

if DEBUG:
    # this app makes it possible to use django as a queue system for celery
    # so you don't need to install RabbitQM or Redis
    # pretty cool for development, but might not suffice for production if your system is heavily used
    # our suggestion is to switch only if you start experiencing issues
    INSTALLED_APPS.append('kombu.transport.django')
    BROKER_URL = 'django://'
    # synchronous behaviour for development
    # more info here: http://docs.celeryproject.org/en/latest/configuration.html#celery-always-eager
    CELERY_ALWAYS_EAGER = True
    CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
else:
    # in production the default background queue manager is Redis
    BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    BROKER_TRANSPORT_OPTIONS = {
        "visibility_timeout": 3600,  # 1 hour
        "fanout_prefix": True
    }
    # in production emails are sent in the background
    EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'

CELERYBEAT_SCHEDULE = {
    'purge_notifications': {
        'task': 'nodeshot.community.notifications.tasks.purge_notifications',
        'schedule': timedelta(days=1),
    }
}

# ------ GRAPPELLI ------ #

if 'grappelli' in INSTALLED_APPS:
    GRAPPELLI_ADMIN_TITLE = '<a href="%s">%s Admin</a>' % (SITE_URL, SITE_NAME)
    GRAPPELLI_INDEX_DASHBOARD = 'nodeshot.dashboard.NodeshotDashboard'

# ------ DEBUG TOOLBAR ------ #

INTERNAL_IPS = ('127.0.0.1', '::1',)  # ip addresses where you want to show the debug toolbar here
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

# ------ UNIT TESTING SPEED UP ------ #

SOUTH_DATABASE_ADAPTERS = {'default': 'south.db.postgresql_psycopg2'}
SOUTH_TESTS_MIGRATE = False

if 'test' in sys.argv:
    CELERY_ALWAYS_EAGER = True

    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.MD5PasswordHasher',
        'django.contrib.auth.hashers.SHA1PasswordHasher',
        'django.contrib.auth.hashers.PBKDF2PasswordHasher',
        'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
        'django.contrib.auth.hashers.BCryptPasswordHasher',
    )

# ------ CORS-HEADERS SETTINGS ------ #

CORS_ORIGIN_ALLOW_ALL = True

# ------ SOCIAL AUTH SETTINGS ------ #

if 'social_auth' in INSTALLED_APPS:
    MIDDLEWARE_CLASSES += ('social_auth.middleware.SocialAuthExceptionMiddleware',)

    # In Django 1.6, the default session serliazer has been switched to one based on JSON,
    # rather than pickles, to improve security. Django-openid-auth does not support this
    # because it attemps to store content that is not JSON serializable in sessions.
    # See https://docs.djangoproject.com/en/dev/releases/1.6/#default-session-serialization-switched-to-json
    # for details on the Django 1.6 change.
    SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'nodeshot.community.profiles.backends.EmailBackend',
        'social_auth.backends.facebook.FacebookBackend',
        'social_auth.backends.google.GoogleOAuth2Backend',
        'nodeshot.community.profiles.social_auth_extra.github.GithubBackend',
    )

    SOCIAL_AUTH_PIPELINE = (
        'social_auth.backends.pipeline.social.social_auth_user',
        'social_auth.backends.pipeline.associate.associate_by_email',
        'social_auth.backends.pipeline.user.get_username',
        'nodeshot.community.profiles.social_auth_extra.pipeline.create_user',
        'social_auth.backends.pipeline.social.associate_user',
        'nodeshot.community.profiles.social_auth_extra.pipeline.load_extra_data',
        'social_auth.backends.pipeline.user.update_user_details'
    )

    SOCIAL_AUTH_ENABLED_BACKENDS = ('facebook', 'google', 'github')

    # register a new app:
    FACEBOOK_APP_ID = ''  # put your app id
    FACEBOOK_API_SECRET = ''
    FACEBOOK_EXTENDED_PERMISSIONS = ['email', 'user_about_me', 'user_birthday', 'user_hometown']

    GOOGLE_OAUTH2_CLIENT_ID = ''
    GOOGLE_OAUTH2_CLIENT_SECRET = ''

    # register a new app:
    GITHUB_APP_ID = ''
    GITHUB_API_SECRET = ''
    GITHUB_EXTENDED_PERMISSIONS = ['user:email']

    SOCIAL_AUTH_DEFAULT_USERNAME = 'new_social_auth_user'
    SOCIAL_AUTH_UUID_LENGTH = 3
    SOCIAL_AUTH_SESSION_EXPIRATION = False
    SOCIAL_AUTH_ASSOCIATE_BY_MAIL = True

    LOGIN_URL = '/'
    LOGIN_REDIRECT_URL = '/'
    LOGIN_ERROR_URL = '/'

# ------ DJANGO-LEAFLET SETTINGS ------ #

LEAFLET_CONFIG = {
    'DEFAULT_CENTER': (49.06775, 30.62011),
    'DEFAULT_ZOOM': 4,
    'MIN_ZOOM': 1,
    'MAX_ZOOM': 18,
    'TILES': [
        ('Map', 'http://otile1.mqcdn.com/tiles/1.0.0/map/{z}/{x}/{y}.png', '&copy; <a href="http://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors | Tiles Courtesy of <a href="http://www.mapquest.com/" target="_blank">MapQuest</a>'),
        ('Satellite', 'http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', 'Source: <a href="http://www.esri.com/">Esri</a> &copy; and the GIS User Community ')
    ],
    'ATTRIBUTION_PREFIX': '<a href="http://github.com/ninuxorg/nodeshot" target="_blank">Nodeshot</a>',
    'RESET_VIEW': False,
}

# ------ DJANGO-ROSETTA SETTINGS ------ #

ROSETTA_CACHE_NAME = 'rosetta'
ROSETTA_MESSAGES_PER_PAGE = 50
ROSETTA_EXCLUDED_APPLICATIONS = [app for app in INSTALLED_APPS if not app.startswith('nodeshot')]
