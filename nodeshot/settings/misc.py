from __future__ import absolute_import
import sys
from .django import INSTALLED_APPS

# ------ GRAPPELLI ------ #

if 'grappelli' in INSTALLED_APPS:
    GRAPPELLI_ADMIN_TITLE = 'Nodeshot Admin'
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
