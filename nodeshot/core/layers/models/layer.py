from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError

from nodeshot.core.base.models import BaseDate
from nodeshot.core.base.choices import MAP_ZOOM, ACCESS_LEVELS
from nodeshot.core.base.utils import choicify

from ..managers import LayerManager


class Layer(BaseDate):
    """ Layer Model """
    name = models.CharField(_('name'), max_length=50, unique=True)
    slug = models.SlugField(max_length=50, db_index=True, unique=True)
    description = models.CharField(_('description'), max_length=250, blank=True, null=True)
    
    # record management
    is_published = models.BooleanField(_('published'), default=True)
    is_external = models.BooleanField(_('is it external?'))
    
    # geographic related fields
    center = models.PointField(_('center coordinates'),null=True, blank=True)
    area = models.PolygonField(_('area'), null=True, blank=True)
    zoom = models.SmallIntegerField(_('default zoom level'), choices=MAP_ZOOM, default=settings.NODESHOT['DEFAULTS']['ZONE_ZOOM'])
    
    # organizational
    organization = models.CharField(_('organization'), help_text=_('Organization which is responsible to manage this layer'), max_length=255)
    website = models.URLField(_('Website'), blank=True, null=True)
    email = models.EmailField(_('email'), help_text=_('possibly an email address that delivers messages to all the active participants; if you don\'t have such an email you can add specific users in the "mantainers" field'), blank=True)
    mantainers = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_('mantainers'), help_text=_('you can specify the users who are mantaining this layer so they will receive emails from the system'), blank=True)
    
    # settings
    minimum_distance = models.IntegerField(default=settings.NODESHOT['DEFAULTS']['ZONE_MINIMUM_DISTANCE'],
                                           help_text=_('minimum distance between nodes, 0 means feature disabled'))
    write_access_level = models.SmallIntegerField(_('write access level'),
                                                  choices=choicify(ACCESS_LEVELS),
                                                  default=ACCESS_LEVELS.get('public'),
                                                  help_text=_('minimum access level to insert new nodes in this layer'))
    # default manager
    objects = LayerManager()
    
    class Meta:
        db_table = 'layers_layer'
        app_label= 'layers'
    
    def __unicode__(self):
        return '%s' % self.name
    
    if 'grappelli' in settings.INSTALLED_APPS:
        @staticmethod
        def autocomplete_search_fields():
            return ('name__icontains', 'slug__icontains')
    
    def clean(self, *args, **kwargs):
        """
        Custom validation
        """
        pass