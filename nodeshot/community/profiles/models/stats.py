from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.base.models import BaseDate
# FIXME
# decouple from net
from nodeshot.networking.net.models import Device
from nodeshot.core.nodes.models import Node
from nodeshot.core.nodes.models.choices import NODE_STATUS
Q = models.Q


class Stats(BaseDate):
    """
    User Statistics Model
    Takes care of counting interesting data of a user
    """
    user = models.OneToOneField(User, verbose_name=_('user'))
    potential_nodes = models.IntegerField(_('potential nodes count'), default=0, help_text=_('status included: potential, planned'))
    active_nodes = models.IntegerField(_('active nodes count'), default=0, help_text=_('status included: active, testing, mantainance'))
    #hotspots = models.IntegerField(_('hotspot count'), default=0, help_text=_('only active nodes'))
    devices = models.IntegerField(_('devices'), default=0)
    
    class Meta:
        db_table = 'profiles_user_statistics'
        verbose_name = _('user statistics')
        verbose_name_plural = _('users statistics')
        app_label= 'profiles'
    
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
    
    #def count_hotspots(self):
    #    """ update user's hotspot count """
    #    self.hotspots = Node.objects.filter(user_id=self.user_id).filter(is_hotspot=True).count()
    #    return self
    
    def count_devices(self):
        """ update user device count """
        self.devices = Device.objects.filter(node__user_id=self.user_id).count()
        return self
    
    def update(self):
        """ update all user statistics """
        self.count_active_nodes().count_potential_nodes().count_devices().save()
        return self
    
    def update_devices(self):
        """ update only device statistics """
        self.count_devices().save()
        return self
    
    def update_nodes(self):
        """ update only node statistics """
        self.count_active_nodes().count_potential_nodes().save()
        return self
    
    @staticmethod
    def update_or_create(user, objects=False):
        """ updates statistics and creates stats record if needed """
        try:
            stats = user.stats
        except Stats.DoesNotExist:
            stats = Stats(user=user)
            stats.save()
        # calls stats.update() if objects == False
        # else calls stats.update_{objects}()
        method_name = 'update' if not objects else 'update_%s' % objects
        # return stats
        return getattr(stats, method_name)()