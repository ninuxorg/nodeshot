from celery import task
#from importlib import import_module
from django.core import management
from django.conf import settings


@task()
def delete_old_notifications():
    """
    deletes old notifications
    """
    management.call_command('delete_old_notifications')


# ------ Asynchronous tasks ------ #


@task
def create_notifications(users, notification_model, notification_type, related_object):
    """
    create notifications in background
    """
    # shortcuts for readability
    Notification = notification_model
    
    # text
    additional = related_object.__dict__ if related_object else ''
    notification_text = settings.NODESHOT['NOTIFICATIONS']['TEXTS'][notification_type] % additional
    
    # loop users, notification settings check is done in Notification model
    for user in users:
        n = Notification(
            to_user=user,
            type=notification_type,
            text=notification_text
        )
        # attach related object if present
        if related_object:
            n.related_object = related_object
        # create notification and send according to user settings
        n.save()