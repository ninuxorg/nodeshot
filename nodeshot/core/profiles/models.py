from django.db import models
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext_lazy as _
from nodeshot.core.base.models import BaseDate
from nodeshot.core.network.models import Device
from nodeshot.core.nodes.models import Node
from nodeshot.core.nodes.models.choices import NODE_STATUS
from choices import SEX_CHOICES
Q = models.Q


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


class Link(BaseDate):
    """
    External links like website or social network profiles
    """
    user = models.ForeignKey(User, verbose_name=_('user'))
    url = models.URLField(_('url'), verify_exists=True)
    description = models.CharField(_('description'), max_length=128, blank=True)
    
    class Meta:
        db_table = 'profiles_link'
    
    def __unicode__(self):
        return self.url


class Stats(BaseDate):
    """
    User Statistics Model
    Takes care of counting interesting data of a user
    """
    user = models.OneToOneField(User, verbose_name=_('user'))
    potential_nodes = models.IntegerField(_('potential nodes count'), default=0, help_text=_('status included: potential, planned'))
    active_nodes = models.IntegerField(_('active nodes count'), default=0, help_text=_('status included: active, testing, mantainance'))
    hotspots = models.IntegerField(_('hotspot count'), default=0, help_text=_('only active nodes'))
    devices = models.IntegerField(_('devices'), default=0)
    
    class Meta:
        db_table = 'profiles_user_statistics'
        verbose_name = _('user statistics')
        verbose_name_plural = _('users statistics')
    
    def __unicode__(self):
        return _(u'Statistics for %s') % self.user.username
    
    def count_active_nodes(self):
        """ update user's active node count """
        status_query = Q(status=NODE_STATUS.get('active')) | Q(status=NODE_STATUS.get('testing')) | Q(status=NODE_STATUS.get('mantainance'))
        self.active_nodes = Node.objects.filter(user_id=self.user_id).filter(status_query).count()
        return self
    
    def count_potential_nodes(self):
        """ update user's potential node count """
        status_query = Q(status=NODE_STATUS.get('potential')) | Q(status=NODE_STATUS.get('planned'))
        self.potential_nodes = Node.objects.filter(user_id=self.user_id).filter(status_query).count()
        return self
    
    def count_hotspots(self):
        """ update user's hotspot count """
        self.hotspots = Node.objects.filter(user_id=self.user_id).filter(is_hotspot=True).count()
        return self
    
    def count_devices(self):
        """ update user device count """
        self.devices = Device.objects.filter(node__user_id=self.user_id).count()
        return self
    
    def update(self):
        """ update all user statistics """
        self.count_active_nodes().count_potential_nodes().count_hotspots().count_devices().save()
        return self
    
    def update_devices(self):
        """ update only device statistics """
        self.count_devices().save()
        return self
    
    def update_nodes(self):
        """ update only device statistics """
        self.count_active_nodes().count_potential_nodes().count_hotspots().save()
        return self
    
    @staticmethod
    def update_or_create(user, objects=False):
        """ updates statistics and creates stats record if needed """
        try:
            stats = user.stats
        except Stats.DoesNotExist:
            stats = Stats(user=user).save()
        # calls stats.update() if objects == False
        # else calls stats.update_<objects>()
        method_name = 'update' if not objects else 'update_%s' % objects
        method = getattr(stats, method_name)()
        return stats

class EmailNotification(BaseDate):
    """
    User Email Notification Model
    Takes care of tracking the user's email notification preferences
    """
    user = models.OneToOneField(User, verbose_name=_('user'))    
    new_potential_node = models.BooleanField(_('notify when a new potential node is added'), default=True)
    new_potential_node_distance = models.IntegerField(_('new potential node added distance range'), default=20,
        help_text=_("""notify only if the new potential node is in a distance of at maximum the value specified (in kilometers).<br />
                    0 means that all the new potential nodes will be notified regardless of the distance."""))
    new_active_node = models.BooleanField(_('notify when a new node is activated'), default=True)
    new_active_node_distance = models.IntegerField(_('new node activated distance range'), default=20,
        help_text=_("""notify only if the new active node is in a distance of at maximum the value specified (in kilometers).<br />
                    0 means that all the new active nodes will be notified regardless of the distance."""))
    receive_outward_emails = models.BooleanField(_('receive important communications regarding the network'), default=True,
        help_text=_("""warning: if you want to deactivate this checkbox ask yourself whether you really belong to this project;<br />
                    not wanting to receive important communications means not caring about this project,
                    therefore it might be a better choice to delete your account."""))
    
    class Meta:
        db_table = 'profiles_email_notification'
    
    def __unicode__(self):
        return _(u'Email Notification Settings for %s') % self.user.username

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


# signals
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

@receiver(post_save, sender=User)
def new_user(sender, **kwargs):
    """ create profile, stat and email_notification objects every time a new user is created """
    created = kwargs['created']
    user = kwargs['instance']
    if created:
        # create profile
        Profile(user=user).save()
        # create statistics
        Stat(user=user).save()
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