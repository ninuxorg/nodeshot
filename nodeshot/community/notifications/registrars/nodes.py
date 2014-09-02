from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
User = get_user_model()

from nodeshot.core.nodes.signals import node_status_changed
from nodeshot.core.nodes.models import Node

from ..settings import settings
from ..models import Notification
from ..tasks import create_notifications


base_queryset = User.objects.filter(is_active=True)


def exclude_owner_of_node(node):
    if node.user_id is not None:
        return base_queryset.exclude(pk=node.user_id)
    else:
        return base_queryset


# ------ NODE CREATED ------ #

@receiver(post_save, sender=Node)
def node_created_handler(sender, **kwargs):
    """ send notification when a new node is created according to users's settings """
    if kwargs['created']:
        obj = kwargs['instance']
        queryset = exclude_owner_of_node(obj)
        create_notifications.delay(**{
            "users": queryset,
            "notification_model": Notification,
            "notification_type": "node_created",
            "related_object": obj
        })


# ------ NODE STATUS CHANGED ------ #

@receiver(node_status_changed)
def node_status_changed_handler(**kwargs):
    """ send notification when the status of a node changes according to users's settings """
    obj = kwargs['instance']
    obj.old_status = kwargs['old_status'].name
    obj.new_status = kwargs['new_status'].name
    queryset = exclude_owner_of_node(obj)
    create_notifications.delay(**{
        "users": queryset,
        "notification_model": Notification,
        "notification_type": "node_status_changed",
        "related_object": obj
    })

    # if node has owner send a different notification to him
    if obj.user is not None:
        create_notifications.delay(**{
            "users": [obj.user],
            "notification_model": Notification,
            "notification_type": "node_own_status_changed",
            "related_object": obj
        })


# ------ NODE DELETED ------ #

@receiver(pre_delete, sender=Node)
def node_deleted_handler(sender, **kwargs):
    """ send notification when a node is deleted according to users's settings """
    obj = kwargs['instance']
    queryset = exclude_owner_of_node(obj)
    create_notifications.delay(**{
        "users": queryset,
        "notification_model": Notification,
        "notification_type": "node_deleted",
        "related_object": obj
    })


# ------ DISCONNECT UTILITY ------ #

def disconnect():
    """ disconnect signals """
    post_save.disconnect(node_created_handler, sender=Node)
    node_status_changed.disconnect(node_status_changed_handler)
    pre_delete.disconnect(node_deleted_handler, sender=Node)


def reconnect():
    """ reconnect signals """
    post_save.connect(node_created_handler, sender=Node)
    node_status_changed.connect(node_status_changed_handler)
    pre_delete.connect(node_deleted_handler, sender=Node)


from nodeshot.core.base.settings import DISCONNECTABLE_SIGNALS
DISCONNECTABLE_SIGNALS.append(
    {
        'disconnect': disconnect,
        'reconnect': reconnect
    }
)
setattr(settings, 'NODESHOT_DISCONNECTABLE_SIGNALS', DISCONNECTABLE_SIGNALS)
