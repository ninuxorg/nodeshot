from settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'nodeshot2',                      # Or path to database file if using sqlite3.
        'USER': 'nodeshot2',                      # Not used with sqlite3.
    }
}