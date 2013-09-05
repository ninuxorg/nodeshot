from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodeshot.networking.net.models import Interface
from nodeshot.networking.net.models.choices import INTERFACE_TYPES


class Tunnel(Interface):
    """ Tunnel Interface """
    sap = models.CharField(max_length=10, null=True, blank=True)
    protocol = models.CharField(max_length=10, help_text=_('eg: GRE'))  # GRE, ... ecc
    endpoint = models.ForeignKey('net.Ip')
    
    objects = Interface.objects.__class__()
    
    class Meta:
        app_label = 'net'
        db_table = 'net_interface_tunnel'
        verbose_name = _('tunnel interface')
        verbose_name_plural = _('tunnel interfaces')
    
    def save(self, *args, **kwargs):
        """ automatically set Interface.type to virtual """
        self.type = INTERFACE_TYPES.get('virtual')
        super(Tunnel, self).save(*args, **kwargs)