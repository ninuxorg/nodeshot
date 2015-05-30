import simplejson as json

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.urlresolvers import reverse
from django.conf import settings

from nodeshot.community.notifications.models import Notification
from ..tasks import send_message


# ------ NEW NOTIFICATIONS ------ #

@receiver(post_save, sender=Notification)
def new_notification_handler(sender, **kwargs):
    if kwargs['created']:
        obj = kwargs['instance']
        message = {
            'user_id': str(obj.to_user.id),
            'model': 'notification',
            'type': obj.type,
            'url': reverse('api_notification_detail', args=[obj.id])
        }
        send_message(json.dumps(message), pipe='private')


# ------ DISCONNECT UTILITY ------ #

def disconnect():
    """ disconnect signals """
    post_save.disconnect(new_notification_handler, sender=Notification)


def reconnect():
    """ reconnect signals """
    post_save.connect(new_notification_handler, sender=Notification)


from nodeshot.core.base.settings import DISCONNECTABLE_SIGNALS
DISCONNECTABLE_SIGNALS.append(
    {
        'disconnect': disconnect,
        'reconnect': reconnect
    }
)
setattr(settings, 'NODESHOT_DISCONNECTABLE_SIGNALS', DISCONNECTABLE_SIGNALS)
