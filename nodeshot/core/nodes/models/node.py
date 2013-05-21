from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from nodeshot.core.base.models import BaseAccessLevel, BaseOrdered
from nodeshot.core.base.managers import GeoAccessLevelPublicManager
from nodeshot.core.base.utils import choicify
from ..signals import node_status_changed

from choices import NODE_STATUS


class Node(BaseAccessLevel):
    """
    Nodes of a network, can be assigned to 'Layers' and should belong to 'Users'
    """
    name = models.CharField(_('name'), max_length=50, unique=True)
    slug = models.SlugField(max_length=50, db_index=True, unique=True)
    status = models.SmallIntegerField(_('status'), max_length=3, choices=choicify(NODE_STATUS), default=NODE_STATUS.get(settings.NODESHOT['DEFAULTS']['NODE_STATUS'], 'potential'))
    is_published = models.BooleanField(default=settings.NODESHOT['DEFAULTS'].get('NODE_PUBLISHED', True))
    
    if 'nodeshot.core.layers' in settings.INSTALLED_APPS:
        # layer might need to be able to be blank, would require custom validation
        layer = models.ForeignKey('layers.Layer')
    
    if 'nodeshot.interoperability' in settings.INSTALLED_APPS:
        # add reference to the external layer's ID
        external_id = models.PositiveIntegerField(blank=True, null=True)
    
    # nodes might be assigned to a foreign layer, therefore user can be left blank, requires custom validation
    user = models.ForeignKey(User, blank=True, null=True)
    
    # area if enabled
    if settings.NODESHOT['SETTINGS']['NODE_AREA']:
        area = models.PolygonField(blank=True, null=True)
    
    # positioning
    coords = models.PointField(_('coordinates'))
    elev = models.FloatField(_('elevation'), blank=True, null=True)
    
    description = models.TextField(_('description'), max_length=255, blank=True, null=True)
    notes = models.TextField(_('notes'), blank=True, null=True)
    
    # manager
    objects = GeoAccessLevelPublicManager()
    
    # this is needed to check if the status is changing
    # explained here:
    # http://stackoverflow.com/questions/1355150/django-when-saving-how-can-you-check-if-a-field-has-changed
    _current_status = None
    
    class Meta:
        db_table = 'nodes_node'
        app_label= 'nodes'
        permissions = (('can_view_nodes', 'Can view nodes'),)
        
        if 'nodeshot.interoperability' in settings.INSTALLED_APPS:
            # the combinations of layer_id and external_id must be unique
            unique_together = ('layer', 'external_id')
    
    def __unicode__(self):
        return '%s' % self.name
    
    def __init__(self, *args, **kwargs):
        """ Fill __current_status """
        super(Node, self).__init__(*args, **kwargs)
        # set current status, but only if it is an existing node
        if self.pk:
            self._current_status = self.status
    
    def save(self, *args, **kwargs):
        """ detect status change """
        super(Node, self).save(*args, **kwargs)
        # if status of a node changes
        if self.status != self._current_status:
            # send django signal
            node_status_changed.send(sender=self, old_status=self._current_status, new_status=self.status)
        # update __current_status
        self._current_status = self.status
    
    if 'grappelli' in settings.INSTALLED_APPS:
        @staticmethod
        def autocomplete_search_fields():
            return ('name__icontains',)