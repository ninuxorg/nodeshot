from netfields import MACAddressField

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from nodeshot.core.base.models import BaseAccessLevel
from choices import INTERFACE_TYPE_CHOICES

HSTORE_ENABLED = settings.NODESHOT['SETTINGS'].get('HSTORE', True)

if HSTORE_ENABLED:
    from django_hstore.fields import DictionaryField, ReferencesField
    from nodeshot.core.base.managers import HStoreAccessLevelManager as InterfaceManager
else:
    from nodeshot.core.base.managers import AccessLevelManager as InterfaceManager


class Interface(BaseAccessLevel):
    """ Interface model """
    device = models.ForeignKey('net.Device')
    type = models.IntegerField(_('type'), max_length=2, choices=INTERFACE_TYPE_CHOICES, blank=True)
    name = models.CharField(_('name'), max_length=10, blank=True, null=True)
    mac = MACAddressField(_('mac address'), max_length=17, unique=True, default=None, null=True, blank=True)
    mtu = models.IntegerField(_('MTU'), blank=True, null=True, default=1500,
                              help_text=_('Maximum Trasmission Unit'))
    tx_rate = models.IntegerField(_('TX Rate'), null=True, default=None, blank=True)
    rx_rate = models.IntegerField(_('RX Rate'), null=True, default=None, blank=True)
    
    # extra data
    if HSTORE_ENABLED:
        data = DictionaryField(_('extra data'), null=True, blank=True,
                            help_text=_('store extra attributes in JSON string'))
        shortcuts = ReferencesField(null=True, blank=True)
    
    objects = InterfaceManager()
    
    class Meta:
        app_label = 'net'
    
    def __unicode__(self):
        return '%s %s' % (self.get_type_display(), self.mac)
    
    def save(self, *args, **kwargs):
        """
        Custom save method does the following:
            * save shortcuts if HSTORE is enabled
        """
        if HSTORE_ENABLED:
            changed = False
            
            if not self.shortcuts.has_key('node'):
                self.shortcuts['node'] = self.device.node
                changed = True
            
            if not self.shortcuts.has_key('user'):
                self.shortcuts['user'] = self.device.node.user
                changed = True
            
            if not self.shortcuts.has_key('layer') and 'nodeshot.core.layers' in settings.INSTALLED_APPS:
                self.shortcuts['layer'] = self.device.node.layer
                changed = True
        
        super(Interface, self).save(*args, **kwargs)
    
    @property
    def owner(self):
        if HSTORE_ENABLED:
            if not self.shortcuts.has_key('user'):
                if self.device or self.device_id:
                    self.save()
                else:
                    raise Exception('Instance does not have a device set yet')
            return self.shortcuts['user']
        else:
            return self.device.node.user
    
    @property
    def node(self):
        if HSTORE_ENABLED:
            if not self.shortcuts.has_key('node'):
                if self.device or self.device_id:
                    self.save()
                else:
                    raise Exception('Instance does not have a device set yet')
            return self.shortcuts['node']
        else:
            return self.device.node
    
    @property
    def layer(self):
        if 'nodeshot.core.layers' not in settings.INSTALLED_APPS:
            return False
        if HSTORE_ENABLED:
            if not self.shortcuts.has_key('layer'):
                if self.device or self.device_id:
                    self.save()
                else:
                    raise Exception('Instance does not have a device set yet')
            return self.shortcuts['layer']
        else:
            return self.device.node.layer
    
    @property
    def ip_addresses(self):
        try:
            addresses = self.data.get('ip_addresses', False)
        # self.data might be none, hence self.data['ip_addresses'] will raise an exception
        except AttributeError:
            addresses = []
        return addresses.replace(' ', '').split(',') if addresses else []
    
    @ip_addresses.setter
    def ip_addresses(self, value):
        """ :param value: a list of ip addresses """
        if not isinstance(value, list):
            raise ValueError('ip_addresses value must be a list')
        # in soem cases self.data might be none, so let's instantiate an empty dict
        if self.data is None:
            self.data = {}
        # update field
        self.data['ip_addresses'] = ', '.join(value)
    
    if 'grappelli' in settings.INSTALLED_APPS:
        @staticmethod
        def autocomplete_search_fields():
            return ('mac__icontains', 'data__icontains')