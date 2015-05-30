from nodeshot.core.base.utils import check_dependencies

check_dependencies(
    dependencies='nodeshot.community.profiles',
    module='nodeshot.community.notifications'
)


from .notification import Notification
from .user_settings import UserEmailNotificationSettings, UserWebNotificationSettings
from ..settings import settings, REGISTER


__all__ = [
    'Notification',
    'UserWebNotificationSettings',
    'UserEmailNotificationSettings'
]


from django.dispatch import receiver
from django.db.models.signals import post_save
from nodeshot.community.profiles.models import Profile


if 'nodeshot.community.notifications' in settings.INSTALLED_APPS:
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
