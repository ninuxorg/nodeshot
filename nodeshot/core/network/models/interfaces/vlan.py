from django.db import models
from django.utils.translation import ugettext_lazy as _
from nodeshot.core.network.models import Interface

class Vlan(Interface):
    tag = models.CharField(max_length=10)
    
    class Meta:
        db_table = 'network_interface_vlan'
        app_label= 'network'
        verbose_name = _('vlan interface')
        verbose_name_plural = _('vlan interfaces')