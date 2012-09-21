from django.db import models
from django.utils.translation import ugettext_lazy as _
from nodeshot.core.base.models import BaseDate
from nodeshot.core.base.choices import ROUTING_PROTOCOLS

class RoutingProtocol(BaseDate):
    name = models.CharField(_('name'), max_length=50, choices=ROUTING_PROTOCOLS)
    version = models.CharField(_('version'), max_length=10, blank=True)
    url = models.URLField(_('url'), blank=True)
    
    class Meta:
        db_table = 'network_routing_protocol'
        app_label= 'network'
    
    def __unicode__(self):
        return '%s %s' % (self.name, self.version)