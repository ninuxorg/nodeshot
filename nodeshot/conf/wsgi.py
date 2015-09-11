# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.

from django.conf import settings
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

# sentry WSGI handler if configured
# more info here: http://raven.readthedocs.org/en/latest/config/django.html#wsgi-middleware
if settings.SENTRY_ENABLED:
    from raven.contrib.django.raven_compat.middleware.wsgi import Sentry
    application = Sentry(application)
