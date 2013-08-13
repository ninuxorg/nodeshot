from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


# profile stuff
def add_notifications(myclass):
    for key, value in settings.NODESHOT['NOTIFICATIONS']['TEXTS'].items():
        # custom notifications cannot be disabled
        if key == 'custom':
            continue
        
        field = models.BooleanField(_(key), default=True)
        field.name = field.column = field.attname = key
        setattr(myclass, key, field)
        myclass.add_to_class(key, field)
    return myclass


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
    
    def __unicode__(self):
        return _('email notification settings for %s') % self.user


@add_notifications
class UserMobileNotificationSettings(models.Model):
    """
    FUNCTIONALITY NOT IMPLEMENTED YET
    User Email Mobile Settings Model
    Takes care of tracking the user's mobile notification preferences
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                verbose_name=_('user'),
                                related_name='mobile_notification_settings')
    
    class Meta:
        app_label = 'notifications'
        db_table = 'notifications_user_mobile_settings'
    
    def __unicode__(self):
        return _('mobile notification settings for %s') % self.user
    
    def __init__(self, *args, **kwargs):
        raise NotImplementedError('Mobile Notifications not implemented yet')