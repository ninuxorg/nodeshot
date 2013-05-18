from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.base.models import BaseDate
from nodeshot.networking.net.models import Device


class Server(BaseDate):
    layer = models.OneToOneField('layers.Layer', verbose_name=_('layer'))
    email = models.EmailField(_('email'), blank=True, null=True)
    url = models.URLField(_('url'))
    devices = models.ManyToManyField(Device, through='MonitoredDevices', verbose_name=_('devices'))
    
    class Meta:
        db_table = 'monitoring_server'


class MonitoredDevices(BaseDate):
    server = models.ForeignKey(Server, verbose_name=_('server'))
    device = models.ForeignKey(Device, verbose_name=_('device'))
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        db_table = 'monitoring_monitored_devices'