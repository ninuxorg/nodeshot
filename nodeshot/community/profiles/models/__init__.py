# this app is dependant on "net"
from django.conf import settings
if 'nodeshot.core.nodes' not in settings.INSTALLED_APPS:
    from nodeshot.core.base.exceptions import DependencyError
    raise DependencyError('nodeshot.community.profiles depends on nodeshot.core.nodes, which should be in settings.INSTALLED_APPS')
    

from profile import Profile
from social_link import SocialLink
from stats import Stats
from email_notification import EmailNotification

__all__ = ['Profile', 'SocialLink', 'Stats', 'EmailNotification']

# Signals
# perform certain actions when some other parts of the application changes
# eg: update user statistics when a new device is added

from django.contrib.auth.models import User, Group
from nodeshot.networking.net.models import Device
from nodeshot.core.nodes.models import Node

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from nodeshot.core.nodes.signals import node_status_changed

@receiver(post_save, sender=User)
def new_user(sender, **kwargs):
    """ create profile, stat and email_notification objects every time a new user is created """
    created = kwargs['created']
    user = kwargs['instance']
    if created:
        # create profile
        Profile(user=user).save()
        # create statistics
        Stats(user=user).save()
        # create notification settings
        EmailNotification(user=user).save()
        # add user to default group
        # TODO: make this configurable in settings
        try:
            default_group = Group.objects.get(name='registered')
            user.groups.add(default_group)
        except Group.DoesNotExist:
            pass
        user.save()

@receiver(post_save, sender=Device)
def new_device(sender, **kwargs):
    """ update user device count when a new device is added """
    created = kwargs['created']
    device = kwargs['instance']
    if created:
        Stats.update_or_create(device.node.user, 'devices')

@receiver(post_delete, sender=Device)
def delete_device(sender, **kwargs):
    """ update user device count when a device is deleted """
    device = kwargs['instance']
    Stats.update_or_create(device.node.user, 'devices')

@receiver(post_save, sender=Node)
def node_changed(sender, **kwargs):
    """ update user node count when a node is saved """
    created = kwargs['created']
    node = kwargs['instance']
    Stats.update_or_create(node.user, 'nodes')

@receiver(post_delete, sender=Node)
def delete_node(sender, **kwargs):
    """ update user node count when a node is deleted """
    node = kwargs['instance']
    Stats.update_or_create(node.user, 'nodes')

# email notifications
#@receiver(node_status_changed)
#def notify_status_changed(sender, **kwargs):
#    """ TODO: write desc """
#    node = sender
#    old_status = kwargs['old_status']
#    new_status = kwargs['new_status']
#    notification_type = EmailNotification.determine_notification_type(old_status, new_status, 'Node')
#    EmailNotification.notify_users(notification_type, node)
#node_status_changed.connect(notify_status_changed)