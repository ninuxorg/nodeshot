# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.

from django.conf import settings


# sentry WSGI handler if configured
# more info here: http://raven.readthedocs.org/en/latest/config/django.html#wsgi-middleware
if getattr(settings, 'RAVEN_CONFIG', {}):
    from raven.contrib.django.raven_compat.middleware.wsgi import Sentry
    from django.core.handlers.wsgi import WSGIHandler
    application = Sentry(WSGIHandler())
# django default wsgi
else:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
