from django.apps import AppConfig as BaseConfig
from django.db.models.signals import post_save
from django.dispatch import receiver

from .settings import REGISTER


class AppConfig(BaseConfig):
    name = 'nodeshot.community.notifications'

    def ready(self):
        from nodeshot.community.profiles.models import Profile

        @receiver(post_save, sender=Profile)
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
