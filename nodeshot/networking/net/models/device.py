from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from nodeshot.core.base.models import BaseAccessLevel

from choices import DEVICE_STATUS, DEVICE_STATUS_CHOICES, DEVICE_TYPES_CHOICES

from django_hstore.fields import DictionaryField, ReferencesField
from nodeshot.core.base.managers import HStoreGeoAccessLevelManager as DeviceManager


class Device(BaseAccessLevel):
    """
    Device Model
    Represents a network device
    eg: an outdoor point-to-point wifi device, a BGP router, a server, and so on
    """
    name = models.CharField(_('name'), max_length=50)
    node = models.ForeignKey('nodes.Node', verbose_name=_('node'))
    type = models.CharField(_('type'), max_length=50, choices=DEVICE_TYPES_CHOICES)
    status = models.SmallIntegerField(_('status'), max_length=2, choices=DEVICE_STATUS_CHOICES, default=DEVICE_STATUS.get('unknown'))
    
    # geographic data
    location = models.PointField(_('location'), blank=True, null=True,
                                 help_text=_("""specify device coordinates (if different from node);
                                    defaults to node coordinates if node is a point,
                                    otherwise if node is a geometry it will default to che centroid of the geometry"""))
    elev = models.FloatField(_('elevation'), blank=True, null=True)
    
    # device specific
    routing_protocols = models.ManyToManyField('net.RoutingProtocol', blank=True)
    
    os = models.CharField(_('operating system'), max_length=128, blank=True, null=True)
    os_version = models.CharField(_('operating system version'), max_length=128, blank=True, null=True)
    
    first_seen = models.DateTimeField(_('first time seen on'), blank=True, null=True, default=None)
    last_seen = models.DateTimeField(_('last time seen on'), blank=True, null=True, default=None)
    
    # text
    description = models.CharField(_('description'), max_length=255, blank=True, null=True)
    notes = models.TextField(_('notes'), blank=True, null=True)
    
    # extra data
    data = DictionaryField(_('extra data'), null=True, blank=True,
                           help_text=_('store extra attributes in JSON string'))
    shortcuts = ReferencesField(null=True, blank=True)
    
    objects = DeviceManager()
    
    # list indicating if any other module has extended this model
    extended_by = []
    
    class Meta:
        app_label = 'net'
        
    def __unicode__(self):
        return '%s' % self.name
    
    def save(self, *args, **kwargs):
        """
        Custom save method does the following:
            * automatically inherit node coordinates and elevation
            * save shortcuts if HSTORE is enabled
        """
        custom_checks = kwargs.pop('custom_checks', True)
        
        super(Device, self).save(*args, **kwargs)
        
        if custom_checks is False:
            return
        
        changed = False
        
        if not self.location:
            self.location = self.node.point
            changed = True
        
        if not self.elev and self.node.elev:
            self.elev = self.node.elev
            changed = True
        
        original_user = self.shortcuts.get('user')
        
        self.shortcuts['user'] = self.node.user
        
        if original_user != self.shortcuts.get('user'):
            changed = True
        
        if 'nodeshot.core.layers' in settings.INSTALLED_APPS:
            original_layer = self.shortcuts.get('layer')
            self.shortcuts['layer'] = self.node.layer
            
            if original_layer != self.shortcuts.get('layer'):
                changed = True
        
        if changed:
            self.save(custom_checks=False)
    
    @property
    def owner(self):
        if 'user' not in self.shortcuts:
            if self.node or self.node_id:
                self.save()
            else:
                raise Exception('Instance does not have a node set yet')
        return self.shortcuts['user']
    
    @property
    def layer(self):
        if 'nodeshot.core.layers' not in settings.INSTALLED_APPS:
            return False
        if 'layer' not in self.shortcuts:
            if self.node or self.node_id:
                self.save()
            else:
                raise Exception('Instance does not have a node set yet')
        return self.shortcuts['layer']
    
    if 'grappelli' in settings.INSTALLED_APPS:
        @staticmethod
        def autocomplete_search_fields():
            return ('name__icontains',)
