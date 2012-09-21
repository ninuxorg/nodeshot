from django.db import models
from django.utils.translation import ugettext_lazy as _
from nodeshot.core.base.models import BaseAccessLevel
from nodeshot.core.base.choices import DEVICE_STATUS, DEVICE_TYPES

class Device(BaseAccessLevel):
    name = models.CharField(_('name'), max_length=50)
    node = models.ForeignKey('nodes.Node', verbose_name=_('node'))
    type = models.CharField(_('type'), max_length=50, choices=DEVICE_TYPES)
    routing_protocols = models.ManyToManyField('network.RoutingProtocol', blank=True)
    status = models.SmallIntegerField(_('status'), max_length=2, choices=DEVICE_STATUS, default=DEVICE_STATUS[1][0])
    firmware = models.CharField(_('firmware'), max_length=40, blank=True, null=True)
    os = models.CharField(_('operating system'), max_length=20, blank=True, null=True)
    description = models.CharField(_('description'), max_length=255, blank=True, null=True)
    notes = models.TextField(_('notes'), blank=True, null=True)
    
    class Meta:
        app_label= 'network'
        permissions = (('can_view_devices', 'Can view devices'),)
        
    def __unicode__(self):
        return '%s' % self.name