from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.conf import settings

from nodeshot.core.nodes.signals import node_status_changed
from nodeshot.core.nodes.models import Node

from ..tasks import send_message


# ------ NODE CREATED ------ #

@receiver(post_save, sender=Node)
def node_created_handler(sender, **kwargs):
    if kwargs['created']:
        obj = kwargs['instance']
        message = 'node "%s" has been added' % obj.name
        send_message.delay(message)

# ------ NODE STATUS CHANGED ------ #

@receiver(node_status_changed)
def node_status_changed_handler(**kwargs):
    obj = kwargs['instance']
    obj.old_status = kwargs['old_status'].name
    obj.new_status = kwargs['new_status'].name
    message = 'node "%s" changed its status from "%s" to "%s"' % (obj.name, obj.old_status, obj.new_status)
    send_message.delay(message)


# ------ NODE DELETED ------ #

@receiver(pre_delete, sender=Node)
def node_deleted_handler(sender, **kwargs):
    obj = kwargs['instance']
    message = 'node "%s" has been deleted' % obj.name
    send_message.delay(message)


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
