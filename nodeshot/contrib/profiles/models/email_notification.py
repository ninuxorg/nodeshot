from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.conf import settings
from nodeshot.core.base.models import BaseDate
from nodeshot.core.nodes.models.choices import NODE_STATUS


class EmailNotification(BaseDate):
    """
    User Email Notification Model
    Takes care of tracking the user's email notification preferences
    """
    user = models.OneToOneField(User, verbose_name=_('user'))    
    new_potential_node = models.BooleanField(_('notify when a new potential node is added'), default=True)
    new_potential_node_distance = models.IntegerField(_('new potential node added distance range'), default=20,
        help_text=_("""notify only if the new potential node is in a distance of at maximum the value specified (in kilometers) from one of my nodes.<br />
                    0 means that all the new potential nodes will be notified regardless of the distance."""))
    new_active_node = models.BooleanField(_('notify when a new node is activated'), default=True)
    new_active_node_distance = models.IntegerField(_('new node activated distance range'), default=20,
        help_text=_("""notify only if the new active node is in a distance of at maximum the value specified (in kilometers) from one of my nodes.<br />
                    0 means that all the new active nodes will be notified regardless of the distance."""))
    receive_outward_emails = models.BooleanField(_('receive important communications regarding the network'), default=True,
        help_text=_("""warning: if you want to deactivate this checkbox ask yourself whether you really belong to this project;<br />
                    not wanting to receive important communications means not caring about this project,
                    therefore it might be a better choice to delete your account."""))
    
    class Meta:
        db_table = 'profiles_email_notification'
        app_label= 'profiles'
    
    def __unicode__(self):
        return _(u'Email Notification Settings for %s') % self.user.username
    
    @staticmethod
    def retrieve_recipients(node, old_status, new_status):
        """ TODO: write desc here """
        # retrieve recipients to notify for a new potential node
        if new_status == NODE_STATUS.get('potential') and old_status == None:
            return User.objects.select_related().filter(is_active=True, emailnotification__new_potential_node=True)#, emailnotification__new_potential_node_distance=0)
        elif new_status == NODE_STATUS.get('active'):
            return User.objects.select_related().filter(is_active=True, emailnotification__new_active_node=True)#, emailnotification__new_active_node_distance=0)
        else:
            # return empty list
            return []
    
    @staticmethod
    def notify_users(old_status, new_status):
        """ TODO: write desc here """
        # retrieve recipients
        recipients = EmailNotification.retrieve_recipients(old_status, new_status)
        # loop over recipients
        for recipient in recipients:
            subject = 'test subject'
            message = 'test message'
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient.email])