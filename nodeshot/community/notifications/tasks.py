from celery import task

from django.core import management
from .settings import TEXTS


@task
def purge_notifications():
    """
    deletes old notifications
    """
    management.call_command('purge_notifications')


# ------ Asynchronous tasks ------ #


@task
def create_notifications(users, notification_model, notification_type, related_object):
    """
    create notifications in a background job to avoid slowing down users
    """
    # shortcuts for readability
    Notification = notification_model

    # text
    additional = related_object.__dict__ if related_object else ''
    notification_text = TEXTS[notification_type] % additional

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
