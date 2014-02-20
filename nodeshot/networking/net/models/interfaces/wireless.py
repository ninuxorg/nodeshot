from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodeshot.networking.net.models import Interface
from nodeshot.networking.net.models.choices import WIRELESS_MODE, WIRELESS_STANDARDS, WIRELESS_CHANNEL, INTERFACE_TYPES


class Wireless(Interface):
    """ Wireless Interface """
    mode = models.CharField(_('wireless mode'), max_length=5,
                            choices=WIRELESS_MODE,
                            blank=True, null=True, default=None)
    standard = models.CharField(_('wireless standard'), max_length=7,
                                choices=WIRELESS_STANDARDS,
                                blank=True, null=True, default=None)
    channel = models.CharField(_('channel'), max_length=4,
                               choices=WIRELESS_CHANNEL,
                               blank=True, null=True, default=None)
    channel_width = models.CharField(_('channel width'), max_length=6,
                                     blank=True, null=True)
    output_power = models.IntegerField(_('output power'), null=True, blank=True)
    dbm = models.IntegerField(_('dBm'), null=True, default=None, blank=True)
    noise = models.IntegerField(_('noise'), null=True, default=None, blank=True)
    
    objects = Interface.objects.__class__()
    
    class Meta:
        app_label = 'net'
        db_table = 'net_interface_wireless'
        verbose_name = _('wireless interface')
        verbose_name_plural = _('wireless interfaces')
    
    def save(self, *args, **kwargs):
        """ automatically set Interface.type to wireless """
        self.type = INTERFACE_TYPES.get('wireless')
        super(Wireless, self).save(*args, **kwargs)