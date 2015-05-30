DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'nodeshot_ci',
        'USER': 'custom_user',
        'PASSWORD': 'custom_password',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

DOMAIN = 'yourcustomhost.com'
