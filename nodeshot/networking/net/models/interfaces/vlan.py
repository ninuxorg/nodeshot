from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodeshot.networking.net.models import Interface
from nodeshot.networking.net.models.choices import INTERFACE_TYPES


class Vlan(Interface):
    """ VLAN """
    tag = models.CharField(max_length=10)
    
    class Meta:
        db_table = 'net_interface_vlan'
        app_label= 'net'
        verbose_name = _('vlan interface')
        verbose_name_plural = _('vlan interfaces')
    
    def save(self, *args, **kwargs):
        """ automatically set Interface.type to virtual """
        self.type = INTERFACE_TYPES.get('virtual')
        super(Vlan, self).save(*args, **kwargs)