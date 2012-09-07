from django.db import models
from django.utils.translation import ugettext_lazy as _
from nodeshot.core.network.models import Interface
from nodeshot.core.base.choices import WIRELESS_STANDARDS

class Wireless(Interface):
    wireless_mode = models.CharField(max_length=5)
    wireless_standard = models.CharField(max_length=7, choices=WIRELESS_STANDARDS)
    wireless_channel = models.CharField(max_length=4, blank=True, null=True)
    channel_width = models.CharField(max_length=6, blank=True, null=True)
    transmitpower = models.IntegerField(null=True, blank=True)
    dbm = models.IntegerField(_('dBm'), null=True, default=None)
    noise = models.IntegerField(_('noise'), null=True, default=None)
    
    class Meta:
        db_table = 'network_interface_wireless'
        app_label= 'network'
        verbose_name = _('wireless interface')
        verbose_name_plural = _('wireless interfaces')