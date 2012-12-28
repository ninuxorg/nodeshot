from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from nodeshot.core.base.models import BaseAccessLevel
from nodeshot.core.base.utils import choicify
from nodeshot.core.nodes.models import Node
from nodeshot.core.network.models import Interface
from choices import METRIC_TYPES, LINK_STATUS, LINK_TYPE


class Link(BaseAccessLevel):
    """ Link Model (both radio and wired links) """
    interface_a = models.ForeignKey(Interface, verbose_name=_('from interface'), related_name='link_interface_from', blank=True, null=True,
                                    help_text=_('mandatory except for "planned" links'))
    interface_b = models.ForeignKey(Interface, verbose_name=_('to interface'), related_name='link_interface_to', blank=True, null=True,
                                    help_text=_('mandatory except for "planned" links'))
    node_a = models.ForeignKey(Node, verbose_name=_('from node'), related_name='link_node_from', blank=True, null=True,
                                    help_text=_('leave blank (except for planned nodes) as it will be filled in automatically if necessary'))
    node_b = models.ForeignKey(Node, verbose_name=_('to node'), related_name='link_node_to', blank=True, null=True,
                               help_text=_('leave blank (except for planned nodes) as it will be filled in automatically if necessary'))
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
    
    def clean(self, *args, **kwargs):
        """
        Custom validation
            1. interface_a and interface_b mandatory except for planned links
            2. planned links should have at least node_a and node_b filled in
            3. dbm and noise fields can be filled only for radio links
        """
        
        if self.status != LINK_STATUS.get('planned') and (self.interface_a == None or self.interface_b == None):
            raise ValidationError(_('fields "from interface" and "to interface" are mandatory in this case'))
        
        if self.status == LINK_STATUS.get('planned') and (self.node_a == None or self.node_b == None):
            raise ValidationError(_('fields "from node" and "to node" are mandatory for planned links'))
        
        if self.dbm != None or self.noise != None:
            raise ValidationError(_('Only links of type "radio" can contain "dbm" and "noise" information'))
    
    def save(self, *args, **kwargs):
        """ Automatically fill 'node_a' and 'node_b' fields if necessary """
        
        if self.interface_a != None:
            self.node_a = self.interface_a.device.node
        
        if self.interface_b != None:
            self.node_b = self.interface_b.device.node
        
        super(Link, self).save(*args, **kwargs)