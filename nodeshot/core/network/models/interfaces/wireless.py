from django.db import models
from django.utils.translation import ugettext_lazy as _
from nodeshot.core.network.models import Interface
from nodeshot.core.base.choices import WIRELESS_MODE, WIRELESS_STANDARDS, WIRELESS_CHANNEL

class Wireless(Interface):
    wireless_mode = models.CharField(max_length=5, choices=WIRELESS_MODE, blank=True)
    wireless_standard = models.CharField(max_length=7, choices=WIRELESS_STANDARDS, blank=True)
    wireless_channel = models.CharField(max_length=4, choices=WIRELESS_CHANNEL, blank=True, null=True)
    channel_width = models.CharField(max_length=6, blank=True, null=True)
    transmitpower = models.IntegerField(null=True, blank=True)
    dbm = models.IntegerField(_('dBm'), null=True, default=None, blank=True)
    noise = models.IntegerField(_('noise'), null=True, default=None, blank=True)
    
    class Meta:
        db_table = 'network_interface_wireless'
        app_label= 'network'
        verbose_name = _('wireless interface')
        verbose_name_plural = _('wireless interfaces')