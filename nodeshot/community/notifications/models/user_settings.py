from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..settings import settings, TEXTS, USER_SETTING, DEFAULT_BOOLEAN, DEFAULT_DISTANCE


def add_notifications(myclass):
    """
    Decorator which adds fields dynamically to User Notification Settings models.

    Each of the keys in the TEXTS dictionary
    are added as a field and DB column.
    """
    for key, value in TEXTS.items():
        # custom notifications cannot be disabled
        if 'custom' in [key, value]:
            continue

        field_type = USER_SETTING[key]['type']

        if field_type == 'boolean':
            field = models.BooleanField(_(key), default=DEFAULT_BOOLEAN)
        elif field_type == 'distance':
            field = models.IntegerField(
                _(key),
                default=DEFAULT_DISTANCE,
                help_text=_('-1 (less than 0): disabled; 0: enabled for all;\
                            1 (less than 0): enabled for those in the specified distance range (km)')
            )
            field.geo_field = USER_SETTING[key]['geo_field']

        field.name = field.column = field.attname = key
        field.user_setting_type = field_type
        setattr(myclass, key, field)
        myclass.add_to_class(key, field)

    return myclass


@add_notifications
class UserWebNotificationSettings(models.Model):
    """
    User Web Notification Settings Model
    Takes care of tracking the user's web notification preferences
    (web notifications are the notifications displayed through the web interface)
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                verbose_name=_('user'),
                                related_name='web_notification_settings')

    class Meta:
        app_label = 'notifications'
        db_table = 'notifications_user_web_settings'
        verbose_name = _('user web notification settings')
        verbose_name_plural = _('user web notification settings')

    def __unicode__(self):
        return _('web notification settings for %s') % self.user


@add_notifications
class UserEmailNotificationSettings(models.Model):
    """
    User Email Notification Settings Model
    Takes care of tracking the user's email notification preferences
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                verbose_name=_('user'),
                                related_name='email_notification_settings')

    class Meta:
        app_label = 'notifications'
        db_table = 'notifications_user_email_settings'
        verbose_name = _('user email notification settings')
        verbose_name_plural = _('user email notification settings')

    def __unicode__(self):
        return _('email notification settings for %s') % self.user
