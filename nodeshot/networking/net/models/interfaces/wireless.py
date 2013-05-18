from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodeshot.networking.net.models import Interface
from nodeshot.networking.net.models.choices import WIRELESS_MODE, WIRELESS_STANDARDS, WIRELESS_CHANNEL, INTERFACE_TYPES


class Wireless(Interface):
    """ Wireless Interface """
    wireless_mode = models.CharField(max_length=5, choices=WIRELESS_MODE, blank=True)
    wireless_standard = models.CharField(max_length=7, choices=WIRELESS_STANDARDS, blank=True)
    wireless_channel = models.CharField(max_length=4, choices=WIRELESS_CHANNEL, blank=True, null=True)
    channel_width = models.CharField(max_length=6, blank=True, null=True)
    transmitpower = models.IntegerField(null=True, blank=True)
    dbm = models.IntegerField(_('dBm'), null=True, default=None, blank=True)
    noise = models.IntegerField(_('noise'), null=True, default=None, blank=True)
    
    class Meta:
        db_table = 'net_interface_wireless'
        app_label= 'net'
        verbose_name = _('wireless interface')
        verbose_name_plural = _('wireless interfaces')
    
    def save(self, *args, **kwargs):
        """ automatically set Interface.type to wireless """
        self.type = INTERFACE_TYPES.get('wireless')
        super(Wireless, self).save(*args, **kwargs)