from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
User = get_user_model()

from .models import UserWebNotificationSettings, UserEmailNotificationSettings
from .settings import REGISTER


@receiver(post_save, sender=User, dispatch_uid='notifications_user_created')
def create_settings(sender, **kwargs):
    """ create user notification settings on user creation """
    created = kwargs['created']
    user = kwargs['instance']
    if created:
        UserWebNotificationSettings.objects.create(user=user)
        UserEmailNotificationSettings.objects.create(user=user)

# ------ register notification signals ------ #

from importlib import import_module

for module in REGISTER:
    import_module(module)
