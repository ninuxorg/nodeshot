from django.conf import settings
from .notification import Notification
from .user_settings import UserEmailNotificationSettings


__all__ = [
    'Notification',
    'UserEmailNotificationSettings'
]


from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
User = get_user_model()

@receiver(post_save, sender=User)
def create_settings(sender, **kwargs):
    """ create user notification settings on user creation """
    created = kwargs['created']
    user = kwargs['instance']
    if created:
        user_email_settings = UserEmailNotificationSettings.objects.create(user=user)


# ------ register notification signals ------ #

from importlib import import_module

for registrar in settings.NODESHOT['NOTIFICATIONS']['REGISTRARS']:
    import_module(registrar)
