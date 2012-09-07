from django.db import models
from django.utils.translation import ugettext_lazy as _
from nodeshot.core.base.models import BaseDate
from nodeshot.core.network.models import Interface

class Vap(BaseDate):
    interface = models.ForeignKey('network.Wireless', verbose_name='wireless interface')
    essid = models.CharField(max_length=50)
    bssid = models.CharField(max_length=50, null=True, blank=True)
    encryption = models.CharField(max_length=50, null=True, blank=True)
    key = models.CharField(max_length=100, null=True, blank=True)
    auth_server = models.CharField(max_length=50, null=True, blank=True)
    auth_port = models.IntegerField(null=True, blank=True)
    accounting_server = models.CharField(max_length=50, null=True, blank=True)
    accounting_port = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'network_interface_vap'
        app_label= 'network'
        verbose_name = _('vap interface')
        verbose_name_plural = _('vap interfaces')