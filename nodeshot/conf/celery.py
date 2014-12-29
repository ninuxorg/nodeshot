from __future__ import absolute_import

import celery

__all__ = ['Celery']


class Celery(celery.Celery):
    """
    send celery exceptions and stacktraces to sentry
    thanks to http://stackoverflow.com/questions/27550916/celery-tasks-uncaught-exceptions-not-being-sent-to-sentry
    """
    def on_configure(self):
        from django.conf import settings
        if hasattr(settings, 'RAVEN_CONFIG') and settings.RAVEN_CONFIG['dsn']:
            import raven
            from raven.contrib.celery import (register_signal,
                                              register_logger_signal)
            client = raven.Client(settings.RAVEN_CONFIG['dsn'])
            register_logger_signal(client)
            register_signal(client)
