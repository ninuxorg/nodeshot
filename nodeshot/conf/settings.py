import os
import sys
from datetime import timedelta
from django.conf import settings

DEBUG = settings.DEBUG
# needed for LiveServerTestCase
if 'test' in sys.argv:
    SERVE_STATIC = True
else:
    SERVE_STATIC = DEBUG
TEMPLATE_DEBUG = DEBUG

USE_I18N = True

USE_L10N = True

USE_TZ = True

# test with StaticLiveServerTestCase
if 'test' in sys.argv:
    DEFAULT_PORT = '8081'
# development
elif DEBUG:
    DEFAULT_PORT = '8000'
# production
else:
    DEFAULT_PORT = '443'

DEFAULT_PROTOCOL = 'http' if DEBUG else 'https'

PORT = getattr(settings, 'PORT', DEFAULT_PORT)
PROTOCOL = getattr(settings, 'PROTOCOL', DEFAULT_PROTOCOL)

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

MEDIA_ROOT = os.path.join(settings.SITE_ROOT, 'media/')
STATIC_ROOT = os.path.join(settings.SITE_ROOT, 'static/')
MEDIA_URL = '/media/'
STATIC_URL = '/static/'
EMAIL_SUBJECT_PREFIX = '[Nodeshot] '

ALLOWED_HOSTS = ['*']

if PROTOCOL == 'https':
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    os.environ['HTTPS'] = 'on'

SENTRY_ENABLED = bool(getattr(settings, 'RAVEN_CONFIG', {}).get('dsn'))

MIDDLEWARE_CLASSES = ['django.middleware.common.CommonMiddleware']

# load sentry-related middleware only if needed
if SENTRY_ENABLED:
    MIDDLEWARE_CLASSES += [
        'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
        'raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware'
    ]

__TMP_MIDDLEWARE__ = [
    ('django.middleware.security.SecurityMiddleware', 'notest'),
    ('django.contrib.sessions.middleware.SessionMiddleware', 'yestest'),
    ('django.middleware.csrf.CsrfViewMiddleware', 'notest'),
    ('django.contrib.auth.middleware.AuthenticationMiddleware', 'yestest'),
    ('django.contrib.auth.middleware.SessionAuthenticationMiddleware', 'notest'),
    ('django.contrib.messages.middleware.MessageMiddleware', 'yestest'),
    ('django.middleware.clickjacking.XFrameOptionsMiddleware', 'notest'),
    ('corsheaders.middleware.CorsMiddleware', 'notest'),
]

# no need to load all the middlewares when running tests
MIDDLEWARE_CLASSES += [entry[0] for entry in __TMP_MIDDLEWARE__ if 'test' not in sys.argv or entry[1] == 'yestest']

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.request",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "social.apps.django_app.context_processors.backends",
    "social.apps.django_app.context_processors.login_redirect",
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
    'nodeshot.community.profiles',
    'nodeshot.core.api',
    'nodeshot.core.layers',
    'nodeshot.core.nodes',
    'nodeshot.core.cms',
    'nodeshot.interop.sync',
    'nodeshot.ui.default',
    'nodeshot.community.mailing',
    'nodeshot.community.participation',
    'nodeshot.community.notifications',
    'nodeshot.networking.net',
    'nodeshot.networking.links',
    'nodeshot.networking.hardware',
    'nodeshot.networking.connectors',
    'nodeshot.interop.open311',
    # admin site
    'grappelli.dashboard',
    'grappelli',
    'filebrowser',
    'django.contrib.admin',
    # 3d party django apps
    'rest_framework',
    'rest_framework_gis',
    'rest_framework_swagger',
    'netfields',
    'leaflet',
    'smuggler',
    'reversion',
    'corsheaders',
    'social.apps.django_app.default',
]

# other utilities
if 'test' not in sys.argv:
    INSTALLED_APPS += [
        'rosetta',
        'django_extensions',
    ]

if 'nodeshot.community.profiles' in INSTALLED_APPS:
    AUTH_USER_MODEL = 'profiles.Profile'
else:
    AUTH_USER_MODEL = 'auth.User'

if SENTRY_ENABLED:
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
        },
        'require_sentry_configured': {
            '()': 'nodeshot.core.base.utils.RequireSentryConfigured'
        }
    },
    'formatters': {
        'verbose': {
            'format': '\n\n[%(levelname)s %(asctime)s] module: %(module)s, process: %(process)d, thread: %(thread)d\n%(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'filters': ['require_sentry_configured']
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
        'mainlog': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': settings.SITE_ROOT + "/../log/nodeshot.error.log",
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 3,
            'formatter': 'verbose'
        },
        'networkinglog': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': settings.SITE_ROOT + "/../log/networking.log",
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 3,
            'formatter': 'verbose'
        },
    },
    'root': {
        'level': 'WARNING',
        'handlers': ['mainlog', 'mail_admins', 'sentry'],
    },
    'loggers': {
        'django': {
            'level': 'ERROR',
            'propagate': True,
        },
        'nodeshot.networking': {
            'handlers': ['networkinglog'],
            'level': 'WARNING',
            'propagate': True,
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
    BROKER_BACKEND = 'memory'
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
    GRAPPELLI_ADMIN_TITLE = '{0} Admin'.format(SITE_NAME)
    GRAPPELLI_INDEX_DASHBOARD = 'nodeshot.dashboard.NodeshotDashboard'

# ------ UNIT TESTING SPEED UP ------ #

if 'test' in sys.argv:
    CELERY_ALWAYS_EAGER = True

    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.MD5PasswordHasher',
    )

# ------ CORS-HEADERS SETTINGS ------ #

CORS_ORIGIN_ALLOW_ALL = True

# ------ SOCIAL AUTH SETTINGS ------ #

if 'social.apps.django_app.default' in INSTALLED_APPS:
    if 'test' not in sys.argv:
        MIDDLEWARE_CLASSES += ('social.apps.django_app.middleware.SocialAuthExceptionMiddleware',)

    AUTHENTICATION_BACKENDS = [
        'django.contrib.auth.backends.ModelBackend',
        'social.backends.facebook.FacebookOAuth2',
        'social.backends.github.GithubOAuth2',
        'social.backends.google.GoogleOAuth2',
    ]

    if 'nodeshot.community.profiles' in INSTALLED_APPS:
        AUTHENTICATION_BACKENDS.insert(1, 'nodeshot.community.profiles.backends.EmailBackend')

    SOCIAL_AUTH_PIPELINE = (
        'social.pipeline.social_auth.social_details',
        'social.pipeline.social_auth.social_uid',
        'social.pipeline.social_auth.auth_allowed',
        'social.pipeline.social_auth.social_user',
        'social.pipeline.user.get_username',
        'social.pipeline.social_auth.associate_by_email',
        'nodeshot.community.profiles.social_auth_extra.pipeline.create_user',
        'social.pipeline.social_auth.associate_user',
        'nodeshot.community.profiles.social_auth_extra.pipeline.load_extra_data',
        'social.pipeline.user.user_details',
    )

    # register a new app:
    SOCIAL_AUTH_FACEBOOK_KEY = ''  # put your app id
    SOCIAL_AUTH_FACEBOOK_SECRET = ''
    SOCIAL_AUTH_FACEBOOK_SCOPE = ['email', 'user_about_me', 'user_birthday', 'user_hometown']

    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = ''
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = ''

    # register a new app:
    SOCIAL_AUTH_GITHUB_KEY = ''
    SOCIAL_AUTH_GITHUB_SECRET = ''
    SOCIAL_AUTH_GITHUB_SCOPE = ['user:email']

    SOCIAL_AUTH_URL_NAMESPACE = 'social'
    SOCIAL_AUTH_USER_MODEL = AUTH_USER_MODEL
    SOCIAL_AUTH_DEFAULT_USERNAME = 'new_social_auth_user'
    SOCIAL_AUTH_UUID_LENGTH = 3
    SOCIAL_AUTH_SESSION_EXPIRATION = False
    SOCIAL_AUTH_ASSOCIATE_BY_MAIL = True
    SOCIAL_AUTH_PROTECTED_USER_FIELDS = ['email']
    SOCIAL_AUTH_FORCE_EMAIL_VALIDATION = True

    SOCIAL_AUTH_LOGIN_URL = '/'
    SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
    SOCIAL_AUTH_LOGIN_ERROR_URL = '/'

# ------ DJANGO-LEAFLET SETTINGS ------ #

LEAFLET_CONFIG = {
    'DEFAULT_CENTER': (49.06775, 30.62011),
    'DEFAULT_ZOOM': 4,
    'MIN_ZOOM': 1,
    'MAX_ZOOM': 18,
    'TILES': [
        ('Map', 'https://a.tile.openstreetmap.org/{z}/{x}/{y}.png', '&copy; <a href="http://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors | Tiles Courtesy of <a href="http://www.mapquest.com/" target="_blank">MapQuest</a>'),
        ('Satellite', 'http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', 'Source: <a href="http://www.esri.com/">Esri</a> &copy; and the GIS User Community ')
    ],
    'ATTRIBUTION_PREFIX': '<a href="http://github.com/ninuxorg/nodeshot" target="_blank">Nodeshot</a>',
    'RESET_VIEW': False,
}

# ------ DJANGO-ROSETTA SETTINGS ------ #

ROSETTA_CACHE_NAME = 'rosetta'
ROSETTA_MESSAGES_PER_PAGE = 50
ROSETTA_EXCLUDED_APPLICATIONS = [app for app in INSTALLED_APPS if not app.startswith('nodeshot')]
