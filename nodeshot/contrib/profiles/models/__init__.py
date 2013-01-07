from profile import Profile
from link import Link
from stats import Stats
from email_notification import EmailNotification

__all__ = ['Profile', 'Link', 'Stats', 'EmailNotification']

# Signals
# perform certain actions when some other parts of the application changes
# eg: update user statistics when a new device is added

from django.contrib.auth.models import User, Group
from nodeshot.core.network.models import Device
from nodeshot.core.nodes.models import Node

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from nodeshot.core.nodes.signals import node_status_changed, hotspot_changed

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
        default_group = Group.objects.get(name='registered')
        user.groups.add(default_group)
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
@receiver(node_status_changed)
def notify_status_changed(sender, **kwargs):
    """ TODO: write desc """
    node = kwargs['sender']
    old_status = kwargs['old_status']
    new_status = kwargs['new_status']
    EmailNotification.notify_users(old_status, new_status)