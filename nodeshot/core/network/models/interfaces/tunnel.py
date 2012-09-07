from django.db import models
from django.utils.translation import ugettext_lazy as _
from nodeshot.core.network.models import Interface

class Tunnel(Interface):
    sap = models.CharField(max_length=10, null=True, blank=True)
    protocol = models.CharField(max_length=10) # GRE, ... ecc
    endpoint = models.ForeignKey('network.Ip', verbose_name=_('ip address'))
    
    class Meta:
        db_table = 'network_interface_tunnel'
        app_label= 'network'
        verbose_name = _('tunnel interface')
        verbose_name_plural = _('tunnel interfaces')