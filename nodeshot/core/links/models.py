from django.db import models
from django.utils.translation import ugettext_lazy as _
from nodeshot.core.base.models import BaseAccessLevel
from nodeshot.core.base.utils import choicify
from nodeshot.core.network.models import Interface
from choices import METRIC_TYPES, LINK_STATUS, LINK_TYPE


class Link(BaseAccessLevel):
    """ Link Model (both radio and wired links) """
    interface_a = models.ForeignKey(Interface, related_name='interface_a')
    interface_b = models.ForeignKey(Interface, related_name='interface_b')
    type = models.SmallIntegerField(_('type'), max_length=10, choices=choicify(LINK_TYPE), default=LINK_TYPE.get('radio'))
    status = models.SmallIntegerField(_('status'), choices=choicify(LINK_STATUS), default=LINK_STATUS.get('planned'))
    metric_type = models.CharField(_('metric type'), max_length=6, choices=choicify(METRIC_TYPES), blank=True)
    metric_value = models.FloatField(_('metric value'), blank=True, null=True)
    tx_rate = models.IntegerField(_('TX rate average'), null=True, default=None, blank=True)
    rx_rate = models.IntegerField(_('RX rate average'), null=True, default=None, blank=True)
    dbm = models.IntegerField(_('dBm average'), null=True, default=None, blank=True)
    noise = models.IntegerField(_('noise average'), null=True, default=None, blank=True)
    
    class Meta:
        permissions = (('can_view_links', 'Can view links'),)
