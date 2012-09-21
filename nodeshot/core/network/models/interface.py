from django.db import models
from django.utils.translation import ugettext_lazy as _
from nodeshot.core.base.models import BaseAccessLevel
from nodeshot.core.base.choices import INTERFACE_TYPE

class Interface(BaseAccessLevel):
    device = models.ForeignKey('network.Device')
    type = models.IntegerField(_('type'), max_length=2, choices=INTERFACE_TYPE)
    name = models.CharField(_('name'), max_length=10, blank=True, null=True)
    mac = models.CharField(_('mac address'), max_length=17, unique=True, default=None)
    mtu = models.IntegerField(_('MTU (Maximum Trasmission Unit)'), blank=True, null=True, default=1500)
    tx_rate = models.IntegerField(_('TX Rate'), null=True, default=None, blank=True)
    rx_rate = models.IntegerField(_('RX Rate'), null=True, default=None, blank=True)
    
    class Meta:
        app_label= 'network'
        permissions = (('can_view_interfaces', 'Can view interfaces'),)
    
    def __unicode__(self):
        return '%s %s' % (self.get_type_display(), self.mac)