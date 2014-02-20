from django.db import models
from django.utils.translation import ugettext_lazy as _

from netfields import InetAddressField

from nodeshot.networking.net.models import Interface
from nodeshot.networking.net.models.choices import INTERFACE_TYPES

from ...managers import NetAccessLevelManager


class Tunnel(Interface):
    """ Tunnel Interface """
    sap = models.CharField(max_length=10, null=True, blank=True)
    protocol = models.CharField(max_length=10, help_text=_('eg: GRE'), blank=True, null=True)
    endpoint = InetAddressField(verbose_name=_('end point'), blank=True, null=True)
    
    objects = NetAccessLevelManager()
    
    class Meta:
        app_label = 'net'
        db_table = 'net_interface_tunnel'
        verbose_name = _('tunnel interface')
        verbose_name_plural = _('tunnel interfaces')
    
    def save(self, *args, **kwargs):
        """ automatically set Interface.type to tunnel """
        self.type = INTERFACE_TYPES.get('tunnel')
        super(Tunnel, self).save(*args, **kwargs)