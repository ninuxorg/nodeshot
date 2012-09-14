from django.db import models
from django.utils.translation import ugettext_lazy as _
from nodeshot.core.network.models import Interface
from nodeshot.core.base.choices import ETHERNET_STANDARDS, DUPLEX_CHOICES

class Ethernet(Interface):
    standard = models.CharField(_('standard'), max_length=15, choices=ETHERNET_STANDARDS)
    duplex = models.CharField(_('duplex?'), max_length=15, choices=DUPLEX_CHOICES)
    
    class Meta:
        db_table = 'network_interface_ethernet'
        app_label= 'network'
        verbose_name = _('ethernet interface')
        verbose_name_plural = _('ethernet interfaces')