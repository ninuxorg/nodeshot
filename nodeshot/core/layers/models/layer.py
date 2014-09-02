from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.gis.measure import D

from django_hstore.fields import DictionaryField

from nodeshot.core.base.models import BaseDate
from nodeshot.core.base.choices import MAP_ZOOM as MAP_ZOOM_CHOICES
from nodeshot.core.nodes.models import Node

from ..settings import settings, ZOOM_DEFAULT, NODE_MINIMUM_DISTANCE
from ..managers import LayerManager
from ..signals import layer_is_published_changed


class Layer(BaseDate):
    """ Layer Model """
    name = models.CharField(_('name'), max_length=50, unique=True)
    slug = models.SlugField(max_length=50, db_index=True, unique=True)
    description = models.CharField(_('description'), max_length=250, blank=True, null=True,
                                   help_text=_('short description of this layer'))
    text = models.TextField(_('extended text'), blank=True, null=True,
                            help_text=_('extended description, specific instructions, links, ecc.'))

    # record management
    is_published = models.BooleanField(_('published'), default=True)
    is_external = models.BooleanField(_('is it external?'), default=False)

    # geographic related fields
    center = models.PointField(_('center coordinates'), null=True, blank=True)
    area = models.PolygonField(_('area'), null=True, blank=True)
    zoom = models.SmallIntegerField(_('default zoom level'), choices=MAP_ZOOM_CHOICES, default=ZOOM_DEFAULT)

    # organizational
    organization = models.CharField(_('organization'), help_text=_('Organization which is responsible to manage this layer'), max_length=255)
    website = models.URLField(_('Website'), blank=True, null=True)
    email = models.EmailField(_('email'),
                              help_text=_("""possibly an email address that delivers messages to all the active participants;
                                          if you don't have such an email you can add specific users in the "mantainers" field"""),
                              blank=True)
    mantainers = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                        verbose_name=_('mantainers'),
                                        help_text=_('you can specify the users who are mantaining this layer so they will receive emails from the system'),
                                        blank=True)

    # settings
    # TODO: rename minimum_distance to nodes_minimum_distance
    minimum_distance = models.IntegerField(default=NODE_MINIMUM_DISTANCE,
                                           help_text=_('minimum distance between nodes in meters, 0 means feature disabled'))
    new_nodes_allowed = models.BooleanField(_('new nodes allowed'), default=True, help_text=_('indicates whether users can add new nodes to this layer'))
    # TODO: HSTORE_SCHEMA setting
    data = DictionaryField(_('extra data'), null=True, blank=True,\
                           help_text=_('store extra attributes in JSON string'))

    # default manager
    objects = LayerManager()

    # this is needed to check if the is_published is changing
    # explained here:
    # http://stackoverflow.com/questions/1355150/django-when-saving-how-can-you-check-if-a-field-has-changed
    _current_is_published = None

    class Meta:
        db_table = 'layers_layer'
        app_label= 'layers'

    def __unicode__(self):
        return '%s' % self.name

    def __init__(self, *args, **kwargs):
        """ Fill __current_is_published """
        super(Layer, self).__init__(*args, **kwargs)
        # set current is_published, but only if it is an existing layer
        if self.pk:
            self._current_is_published = self.is_published

    def save(self, *args, **kwargs):
        """
        intercepts changes to is_published and fires layer_is_published_changed signal
        """
        super(Layer, self).save(*args, **kwargs)

        # if is_published of an existing layer changes
        if self.pk and self.is_published != self._current_is_published:
            # send django signal
            layer_is_published_changed.send(
                sender=self.__class__,
                instance=self,
                old_is_published=self._current_is_published,
                new_is_published=self.is_published
            )
            # unpublish nodes
            self.update_nodes_published()

        # update _current_is_published
        self._current_is_published = self.is_published

    def update_nodes_published(self):
        """ publish or unpublish nodes of current layer """
        if self.pk:
            self.node_set.all().update(is_published=self.is_published)

    if 'grappelli' in settings.INSTALLED_APPS:
        @staticmethod
        def autocomplete_search_fields():
            return ('name__icontains', 'slug__icontains')


# ------ Add Layer related methods to Node class ------ #

@property
def intersecting_layers(self):
    return Layer.objects.filter(area__contains=self.point)

Node.intersecting_layers = intersecting_layers


# ------ Additional validation for Node model ------ #

def new_nodes_allowed_for_layer(self):
    """
    ensure new nodes are allowed for this layer
    """
    try:
        if not self.pk and not self.layer.new_nodes_allowed:
            raise ValidationError(_('New nodes are not allowed for this layer'))
    except ObjectDoesNotExist:
        # this happens if node.layer is None
        return

# TODO: thes features must be tested inside the layer's app code (nodeshot.core.layers.tests)
def node_layer_validation(self):
    """
    1. if minimum distance is specified, ensure node is not too close to other nodes;
    2. if layer defines an area, ensure node coordinates are contained in the area
    """
    try:
        minimum_distance = self.layer.minimum_distance
        geometry = self.geometry
        layer_area = self.layer.area
    except ObjectDoesNotExist:
        # this happens if node.layer is None
        return

    # TODO - lower priority: do this check only when coordinates are changing
    if minimum_distance > 0:
        near_nodes = Node.objects.exclude(pk=self.id).filter(geometry__distance_lte=(geometry, D(m=minimum_distance))).count()
        if near_nodes > 0 :
            raise ValidationError(_('Distance between nodes cannot be less than %s meters') % minimum_distance)

    if layer_area is not None and not layer_area.contains(geometry):
        raise ValidationError(_('Node must be inside layer area'))

Node.add_validation_method(new_nodes_allowed_for_layer)
Node.add_validation_method(node_layer_validation)
