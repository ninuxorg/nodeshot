from nodeshot.core.base.utils import check_dependencies

check_dependencies(
    dependencies='emailconfirmation',
    module='nodeshot.community.profiles'
)


from profile import Profile
from social_link import SocialLink

__all__ = ['Profile', 'SocialLink']

# Signals
# perform certain actions when some other parts of the application changes
# eg: update user statistics when a new device is added

from django.contrib.auth.models import Group
from django.dispatch import receiver
from django.db.models.signals import post_save
#from nodeshot.core.nodes.signals import node_status_changed

@receiver(post_save, sender=Profile)
def new_user(sender, **kwargs):
    """ operations to be performed each time a new user is created """
    created = kwargs['created']
    user = kwargs['instance']
    if created:
        # add user to default group
        # TODO: make this configurable in settings
        try:
            default_group = Group.objects.get(name='registered')
            user.groups.add(default_group)
        except Group.DoesNotExist:
            pass
        user.save()


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