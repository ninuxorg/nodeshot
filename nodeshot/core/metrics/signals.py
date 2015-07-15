from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models.signals import pre_migrate
User = get_user_model()

from .utils import create_database, write


@receiver(pre_migrate, dispatch_uid='create_inflxudb_database')
def create_database_signal(sender, **kwargs):
    create_database()


@receiver(user_logged_in, dispatch_uid='metrics_user_loggedin')
def user_loggedin(sender, **kwargs):
    """ collect metrics about user logins """
    values = {
        'value': 1,
        'path': kwargs['request'].path,
        'user_id': str(kwargs['user'].pk),
        'username': kwargs['user'].username,
    }
    write('user_logins', values=values)


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
