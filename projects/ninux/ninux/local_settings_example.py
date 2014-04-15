# Django local settings for nodeshot project.

APP_PATH = '/home/stefano/django/nodeshot/'
DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'nodeshot',                      # Or path to database file if using sqlite3.
        'USER': 'postgres',                      # Not used with sqlite3.
        'PASSWORD': 'postgres',                  # Not used with sqlite3.
        'HOST': '127.0.0.1',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}
DOMAIN = 'localhost'
ALLOWED_HOSTS = ['*'] 
SECRET_KEY = 'da)t*+$)ugeyip6-#tuyy$5wf2ervc0d2n#h)qb)y5@ly$t*@w'

