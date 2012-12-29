from django.db import models
from django.utils.translation import ugettext_lazy as _
from nodeshot.core.base.models import BaseAccessLevel
from nodeshot.core.base.managers import AccessLevelManager
from choices import DEVICE_STATUS, DEVICE_STATUS_CHOICES, DEVICE_TYPES_CHOICES


class Device(BaseAccessLevel):
    """
    Device Model
    Represents a network device, eg: an outdoor point-to-point wifi device, a BGP router, a server, and so on
    """
    name = models.CharField(_('name'), max_length=50)
    node = models.ForeignKey('nodes.Node', verbose_name=_('node'))
    type = models.CharField(_('type'), max_length=50, choices=DEVICE_TYPES_CHOICES)
    routing_protocols = models.ManyToManyField('network.RoutingProtocol', blank=True)
    status = models.SmallIntegerField(_('status'), max_length=2, choices=DEVICE_STATUS_CHOICES, default=DEVICE_STATUS.get('unplugged'))
    firmware = models.CharField(_('firmware'), max_length=40, blank=True, null=True)
    os = models.CharField(_('operating system'), max_length=20, blank=True, null=True)
    description = models.CharField(_('description'), max_length=255, blank=True, null=True)
    notes = models.TextField(_('notes'), blank=True, null=True)
    
    objects = AccessLevelManager()
    
    class Meta:
        app_label= 'network'
        permissions = (('can_view_devices', 'Can view devices'),)
        
    def __unicode__(self):
        return '%s' % self.name