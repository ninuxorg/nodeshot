from django.db import models
from django.contrib.auth.models import User
from nodeshot.core.base.models import BaseAccessLevel, BaseOrdered
from nodeshot.core.base.choices import NODE_STATUS
from django.utils.translation import ugettext_lazy as _

class Node(BaseAccessLevel):
    """
    Nodes of a network, can be assigned to 'Zones' and should belong to 'Users'
    """
    name = models.CharField(_('name'), max_length=50, unique=True)
    status = models.SmallIntegerField(_('status'), max_length=3, choices=NODE_STATUS, default=0) # todo: default status configurable
    slug = models.SlugField(max_length=50, db_index=True, unique=True)
    
    # zone might need to be able to be blank, would require custom validation
    zone = models.ForeignKey('zones.Zone', blank=True)
    # nodes might be assigned to a foreign zone, therefore user can be left blank, requires custom validation
    user = models.ForeignKey(User, blank=True, null=True)
    
    # positioning
    lat = models.FloatField(_('latitude'))
    lng = models.FloatField(_('longitude')) 
    elev = models.FloatField(_('elevation'), blank=True, null=True)
    
    is_hotspot = models.BooleanField(_('is it a hotspot?'), default=False)
    description = models.CharField(_('description'), max_length=255, blank=True, null=True)
    notes = models.TextField(_('notes'), blank=True, null=True)
    
    class Meta:
        db_table = 'nodes_node'
        app_label= 'nodes'
        permissions = (('can_view_nodes', 'Can view nodes'),)
    
    def __unicode__(self):
        return '%s' % self.name