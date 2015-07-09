from django.apps import AppConfig as BaseConfig
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models.signals import post_syncdb
from django.contrib.auth import models

from .utils import create_database


class AppConfig(BaseConfig):
    name = 'nodeshot.core.metrics'

    def ready(self):
        def create_database_signal(sender, **kwargs):
            create_database()

        post_syncdb.connect(create_database_signal, sender=models)

        User = get_user_model()

        @receiver(user_logged_in, dispatch_uid='metrics_user_loggedin')
        def user_loggedin(sender, **kwargs):
            """ collect metrics about user logins """
            tags = {
                'user_id': str(kwargs['user'].pk),
                'username': kwargs['user'].username,
            }
            values = {
                'value': 1,
                'path': kwargs['request'].path
            }
            write('user_logins', values=values, tags=tags)

        @receiver(post_delete, sender=User, dispatch_uid='metrics_user_created')
        def user_created(sender, **kwargs):
            """ collect metrics about users unsubscribing """
            write('user_variations', {'variation': -1}, tags={'action': 'deleted'})
            write('user_count', {'total': User.objects.count()})

        @receiver(post_save, sender=User, dispatch_uid='metrics_user_deleted')
        def user_deleted(sender, **kwargs):
            """ collect metrics about new users signing up """
            if kwargs.get('created'):
                write('user_variations', {'variation': 1}, tags={'action': 'created'})
                write('user_count', {'total': User.objects.count()})
