from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from nodeshot.core.base.models import BaseDate
from choices import SEX_CHOICES


class Profile(BaseDate):
    """
    User Profile Model
    Contains the personal info of a user
    """
    user = models.OneToOneField(User, verbose_name=_('user'))
    gender = models.CharField(_('gender'), max_length=1, choices=SEX_CHOICES, blank=True)
    birth_date = models.DateField(_('birth date'), blank=True, null=True)
    city = models.CharField(_('city'), max_length=30, blank=True)
    about = models.TextField(_('about me'), blank=True)
    
    def __unicode__(self):
        return self.user.username


class ExternalLink(BaseDate):
    """
    External links like website or social network profiles
    """
    user = models.ForeignKey(User, verbose_name=_('user'))
    url = models.URLField(_('url'), verify_exists=True)
    description = models.CharField(_('description'), max_length=128, blank=True)


class Stat(BaseDate):
    """
    User Statistics Model
    Takes care of counting interesting data of a user
    """
    user = models.OneToOneField(User, verbose_name=_('user'))
    nodes = models.IntegerField(_('nodes count'), default=0)
    devices = models.IntegerField(_('devices'), default=0)
    
    def __unicode__(self):
        return _(u'Statistics for %s') % self.user.username


class EmailNotification(BaseDate):
    """
    User Email Notification Model
    Takes care of tracking the user's email notification preferences
    """
    user = models.OneToOneField(User, verbose_name=_('user'))    
    new_potential_node = models.BooleanField(_('notify when a new potential node is added'), default=True)
    new_potential_node_distance = models.IntegerField(_('new potential node added distance range'), default=20,
        help_text=_("""notify only if the new potential node is in a distance of at maximum the value specified (in kilometers).
                    \n\n0 means that all the new potential nodes will be notified regardless of the distance."""))
    new_active_node = models.BooleanField(_('notify when a new node is activated'), default=True)
    new_active_node_distance = models.IntegerField(_('new node activated distance range'), default=20,
        help_text=_("""notify only if the new active node is in a distance of at maximum the value specified (in kilometers).
                    \n\n0 means that all the new active nodes will be notified regardless of the distance."""))
    receive_outward_emails = models.BooleanField(_('receive important communications regarding the network'), default=True,
        help_text=_("""warning: if you want to deactivate this checkbox ask yourself whether you really belong to this project;
                    not wanting to receive important communications means not caring about this project,
                    therefore it might be a better choice to delete your account."""))
    
    class Meta:
        db_table = 'profile_email_notification'

#class MobileNotification(models.Model):
#    """
#    User Mobile Notification Model
#    Takes care of tracking the user's mobile notification preferences
#    """
#    user = models.OneToOneField(User, verbose_name=_('user'))
#    # TODO
#    
#    class Meta:
#        db_table = 'profile_mobile_notification'