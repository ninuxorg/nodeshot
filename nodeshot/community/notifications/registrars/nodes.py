from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings

from nodeshot.core.nodes.signals import node_status_changed
from nodeshot.core.nodes.models import Node

from ..models import *


@receiver(post_save, sender=Node)
def node_created(sender, **kwargs):
    """ send notification when a new node is created according to users's settings"""
    created = kwargs['created']
    node = kwargs['instance']
    
    if created:
        
        email_settings = UserEmailNotificationSettings.objects.filter(node_created=True).only(
            'node_created', 'user'
        )
        
        for email_setting in email_settings:
            n = Notification(
                to_user_id=email_setting.user_id,
                type='node_created',
                text=settings.NODESHOT['NOTIFICATIONS']['TEXTS']['node_created'] % node.__dict__
            )
            n.save()