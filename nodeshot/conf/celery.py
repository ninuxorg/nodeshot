from __future__ import absolute_import

import os
import celery
from django.conf import settings


__all__ = ['Celery', 'init_celery']


class Celery(celery.Celery):
    """
    send celery exceptions and stacktraces to sentry
    thanks to http://stackoverflow.com/questions/27550916/celery-tasks-uncaught-exceptions-not-being-sent-to-sentry
    """
    def on_configure(self):
        if hasattr(settings, 'RAVEN_CONFIG') and settings.RAVEN_CONFIG['dsn']:
            import raven
            from raven.contrib.celery import (register_signal,
                                              register_logger_signal)
            client = raven.Client(settings.RAVEN_CONFIG['dsn'])
            register_logger_signal(client)
            register_signal(client)


def init_celery(project_name):
    """ init celery app without the need of redundant code """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', '%s.settings' % project_name)
    app = Celery(project_name)
    app.config_from_object('django.conf:settings')
    app.autodiscover_tasks(settings.INSTALLED_APPS, related_name='tasks')
    return app
