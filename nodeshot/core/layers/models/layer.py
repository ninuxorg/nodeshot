from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.gis.measure import D
from django.contrib.gis.geos import Polygon, Point, GEOSException

from django_hstore.fields import DictionaryField

from nodeshot.core.base.models import BaseDate
from nodeshot.core.nodes.models import Node

from ..settings import settings, NODES_MINIMUM_DISTANCE, HSTORE_SCHEMA
from ..managers import LayerManager
from ..signals import layer_is_published_changed


class Layer(BaseDate):
    """
    Layer Model
    A layer represent a categorization of nodes.
    Layers might have geographical boundaries and might be managed by certain organizations.
    """
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
    area = models.GeometryField(_('area'), help_text=_('If a polygon is used nodes of this layer will have to be contained in it.\
                                                        If a point is used nodes of this layer can be located anywhere. Lines are not allowed.'))
    # organizational
    organization = models.CharField(_('organization'), max_length=255, blank=True,
                                    help_text=_('Organization which is responsible to manage this layer'))
    website = models.URLField(_('Website'), blank=True, null=True)
    email = models.EmailField(_('email'), blank=True,
                              help_text=_("""possibly an email address that delivers messages to all the active participants;
                                          if you don't have such an email you can add specific users in the "mantainers" field"""))
    mantainers = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_('mantainers'), blank=True,
                                        help_text=_('you can specify the users who are mantaining this layer so they will receive emails from the system'))
    # settings
    nodes_minimum_distance = models.IntegerField(default=NODES_MINIMUM_DISTANCE,
                                                 help_text=_('minimum distance between nodes in meters, 0 means there is no minimum distance'))
    new_nodes_allowed = models.BooleanField(_('new nodes allowed'), default=True, help_text=_('indicates whether users can add new nodes to this layer'))
    data = DictionaryField(_('extra data'), schema=HSTORE_SCHEMA, null=True, editable=False)

    # default manager
    objects = LayerManager()

    # this is needed to check if the is_published is changing
    # explained here:
    # http://stackoverflow.com/questions/1355150/django-when-saving-how-can-you-check-if-a-field-has-changed
    _current_is_published = None

    class Meta:
        db_table = 'layers_layer'
        app_label = 'layers'

    def __unicode__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        """ Fill _current_is_published """
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

    def clean(self):
        """
        Ensure area is either a Point or a Polygon
        """
        if not isinstance(self.area, (Polygon, Point)):
            raise ValidationError('area can be only of type Polygon or Point')

    @property
    def center(self):
        # if area is point just return that
        if isinstance(self.area, Point) or self.area is None:
            return self.area
        # otherwise return point_on_surface or centroid
        try:
            # point_on_surface guarantees that the point is within the geometry
            return self.area.point_on_surface
        except GEOSException:
            # fall back on centroid which may not be within the geometry
            # for example, a horseshoe shaped polygon
            return self.area.centroid

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
    if not self.pk and self.layer and not self.layer.new_nodes_allowed:
        raise ValidationError(_('New nodes are not allowed for this layer'))


def nodes_minimum_distance_validation(self):
    """
    if minimum distance is specified, ensure node is not too close to other nodes;
    """
    if self.layer and self.layer.nodes_minimum_distance:
        minimum_distance = self.layer.nodes_minimum_distance
        # TODO - lower priority: do this check only when coordinates are changing
        near_nodes = Node.objects.exclude(pk=self.id).filter(geometry__distance_lte=(self.geometry, D(m=minimum_distance))).count()
        if near_nodes > 0:
            raise ValidationError(_('Distance between nodes cannot be less than %s meters') % minimum_distance)


def node_contained_in_layer_area_validation(self):
    """
    if layer defines an area, ensure node coordinates are contained in the area
    """
    # if area is a polygon ensure it contains the node
    if self.layer and isinstance(self.layer.area, Polygon) and not self.layer.area.contains(self.geometry):
        raise ValidationError(_('Node must be inside layer area'))


Node.add_validation_method(new_nodes_allowed_for_layer)
Node.add_validation_method(nodes_minimum_distance_validation)
Node.add_validation_method(node_contained_in_layer_area_validation)
