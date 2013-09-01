from django.contrib.gis.db import models
from django.contrib.gis.geos import LineString
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from django_hstore.fields import DictionaryField, ReferencesField

from nodeshot.core.base.managers import HStoreGeoAccessLevelManager as LinkManager
from nodeshot.core.base.models import BaseAccessLevel
from nodeshot.core.base.utils import choicify
from nodeshot.core.nodes.models import Node
from nodeshot.networking.net.models import Interface

from choices import METRIC_TYPES, LINK_STATUS, LINK_TYPE


class Link(BaseAccessLevel):
    """
    Link Model
    Intended for both wireless and wired links
    """
    status = models.SmallIntegerField(_('status'), choices=choicify(LINK_STATUS), default=LINK_STATUS.get('planned'))
    
    # in most cases these two fields are mandatory, except for "planned" links
    interface_a = models.ForeignKey(Interface, verbose_name=_('from interface'),
                  related_name='link_interface_from', blank=True, null=True,
                  help_text=_('mandatory except for "planned" links (in planned links you might not have any device installed yet)'))
    interface_b = models.ForeignKey(Interface, verbose_name=_('to interface'),
                  related_name='link_interface_to', blank=True, null=True,
                  help_text=_('mandatory except for "planned" links (in planned links you might not have any device installed yet)'))
    
    # in "planned" links these two are necessary
    node_a = models.ForeignKey(Node, verbose_name=_('from node'),
                  related_name='link_node_from', blank=True, null=True,
                  help_text=_('leave blank (except for planned nodes) as it will be filled in automatically'))
    node_b = models.ForeignKey(Node, verbose_name=_('to node'),
                  related_name='link_node_to', blank=True, null=True,
                  help_text=_('leave blank (except for planned nodes) as it will be filled in automatically'))
    
    line = models.LineStringField(blank=True, null=True,
                           help_text=_('leave blank and the line will be drawn automatically'))
    
    type = models.SmallIntegerField(_('type'), max_length=10, choices=choicify(LINK_TYPE), default=LINK_TYPE.get('radio'))
    metric_type = models.CharField(_('metric type'), max_length=6, choices=choicify(METRIC_TYPES), blank=True)
    metric_value = models.FloatField(_('metric value'), blank=True, null=True)
    tx_rate = models.IntegerField(_('TX rate average'), null=True, default=None, blank=True)
    rx_rate = models.IntegerField(_('RX rate average'), null=True, default=None, blank=True)
    dbm = models.IntegerField(_('dBm average'), null=True, default=None, blank=True)
    noise = models.IntegerField(_('noise average'), null=True, default=None, blank=True)
    
    data = DictionaryField(_('extra data'), null=True, blank=True,
                            help_text=_('store extra attributes in JSON string'))
    shortcuts = ReferencesField(null=True, blank=True)
    
    # manager
    objects = LinkManager()
    
    def __unicode__(self):
        return _(u'Link between %s and %s') % (self.node_a_name, self.node_b_name)
    
    def clean(self, *args, **kwargs):
        """
        Custom validation
            1. interface_a and interface_b mandatory except for planned links
            2. planned links should have at least node_a and node_b filled in
            3. dbm and noise fields can be filled only for radio links
            4. interface_a and interface_b must differ
        """
        
        if self.status != LINK_STATUS.get('planned') and (self.interface_a == None or self.interface_b == None):
            raise ValidationError(_('fields "from interface" and "to interface" are mandatory in this case'))
        
        if self.status == LINK_STATUS.get('planned') and (self.node_a == None or self.node_b == None):
            raise ValidationError(_('fields "from node" and "to node" are mandatory for planned links'))
        
        if self.dbm != None or self.noise != None:
            raise ValidationError(_('Only links of type "radio" can contain "dbm" and "noise" information'))
        
        if (self.interface_a_id == self.interface_b_id) or (self.interface_a == self.interface_b):
            raise ValidationError(_('link cannot have same "from interface" and "to interface"'))
    
    def save(self, *args, **kwargs):
        """
        Custom save does the following:
            * automatically fill 'node_a' and 'node_b' fields if necessary
            * draw line between two nodes
            * fill shortcut properties node_a_name and node_b_name
        """
        
        # fill in node_a and node_b
        if self.node_a is None and self.interface_a != None:
            self.node_a = self.interface_a.node
        if self.node_b is None and self.interface_b != None:
            self.node_b = self.interface_b.node
        
        # draw linestring
        if not self.line:
            self.line = LineString(self.node_a.point, self.node_b.point)
        
        # fill properties
        if self.data is None or self.data.get('node_a_name', None) is None:
            self.data = self.data or {}  # in case is None init empty dict
            self.data['node_a_name'] = self.node_a.name
            self.data['node_b_name'] = self.node_b.name
        
        super(Link, self).save(*args, **kwargs)
    
    @property
    def node_a_name(self):
        self.data = self.data or {}
        return self.data.get('node_a_name', None)
    
    @property
    def node_b_name(self):
        self.data = self.data or {}
        return self.data.get('node_b_name', None)