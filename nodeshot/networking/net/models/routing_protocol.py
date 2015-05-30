from django.db import models
from django.utils.translation import ugettext_lazy as _
from nodeshot.core.base.models import BaseDate
from choices import ROUTING_PROTOCOLS


class RoutingProtocol(BaseDate):
    """ Routing Protocol Model """
    name = models.CharField(_('name'), max_length=50, choices=ROUTING_PROTOCOLS)
    version = models.CharField(_('version'), max_length=128, blank=True)
    
    class Meta:
        app_label = 'net'
        db_table = 'net_routing_protocol'
        unique_together = ('name', 'version')
    
    def __unicode__(self):
        return '%s %s' % (self.name, self.version)