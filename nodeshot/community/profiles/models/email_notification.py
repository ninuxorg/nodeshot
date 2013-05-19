from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from nodeshot.core.base.models import BaseDate
from nodeshot.core.base.utils import get_key_by_value
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
    def determine_notification_type(old_status, new_status, sender='Node'):
        if new_status == NODE_STATUS.get(settings.NODESHOT['DEFAULTS']['NODE_STATUS']) and old_status == None and sender == 'Node':
            return 'new_node'
        elif new_status == NODE_STATUS.get('active') and old_status != None and sender == 'Node':
            return 'node_activated'
        elif old_status != None and sender == 'Node':
            return 'node_changing_status'
        #elif sender == 'Hotspot' and (old_status == False or old_status == None) and new_status == True:
        #    return 'new_hotspot'
        #elif sender == 'Hotspot' and old_status == True and new_status == False:
        #    return 'hotspot_removed'
    
    @staticmethod
    def retrieve_recipients(notification_type, updated_node):
        """ TODO: write desc here """
        # retrieve recipients to notify for a new potential node
        if notification_type == 'new_node':
            # TODO: needs cleanup, new_potential_node should be new_node
            return User.objects.select_related().filter(is_active=True, emailnotification__new_potential_node=True)#, emailnotification__new_potential_node_distance=0)
        elif notification_type == 'node_activated':
            return User.objects.select_related().filter(is_active=True, emailnotification__new_active_node=True)#, emailnotification__new_active_node_distance=0)
        else:
            # return empty list
            return []
    
    @staticmethod
    def notify_users(notification_type, updated_node):
        """ TODO: write desc here """
        # retrieve recipients
        users = EmailNotification.retrieve_recipients(notification_type, updated_node)
        
        # if no users return here
        if not len(users) > 0:
            return False
        
        # context that will be passed to render_to_string, these keys are the same for each iteration
        context = {
            'site_name': settings.SITE_NAME,
            'site_url': settings.SITE_URL,
            'node': updated_node,
        }
        
        # loop over recipients
        for user in users:
            # rare case but it could happen while testing
            if not user.email:
                continue
            # obviously this part of the context is different for each user
            context['user'] = user
            # render subject
            subject = render_to_string('email_notifications/%s_subject.txt' % notification_type, context)
            # render message body
            message = render_to_string('email_notifications/%s_body.txt' % notification_type, context)
            # send mail
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        # return notified users
        return users