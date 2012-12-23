from django.db import models
from django.utils.translation import ugettext_lazy as _
from nodeshot.core.network.models import Interface
from nodeshot.core.network.models.choices import INTERFACE_TYPES


class Bridge(Interface):
    """ Bridge interface """
    interfaces = models.ManyToManyField(Interface, verbose_name=_('interfaces'), related_name='bridge_interfaces')
    
    class Meta:
        db_table = 'network_interface_bridge'
        app_label= 'network'
        verbose_name = _('bridge interface')
        verbose_name_plural = _('bridge interfaces')
    
    def save(self, *args, **kwargs):
        """ automatically set Interface.type to bridge """
        self.type = INTERFACE_TYPES.get('bridge')
        super(Bridge, self).save(*args, **kwargs)