from django.db import models
from django.contrib.auth.models import User
from nodeshot.core.base.models import BaseDate, BaseAccessLevel, BaseOrdered
from nodeshot.core.base.choices import TIME_ZONES, NODE_STATUS
from django.utils.translation import ugettext_lazy as _

class Zone(BaseDate):
    name = models.CharField(_('name'), max_length=50, unique=True)
    parent = models.ForeignKey('Zone', blank=True, null=True)
    time_zone = models.CharField(_('time zone'), max_length=8, choices=TIME_ZONES)
    description = models.CharField(_('description'), max_length=250, blank=True, null=True)
    slug = models.SlugField(max_length=50, db_index=True, unique=True)
    lat = models.FloatField(_('center latitude'))
    lng = models.FloatField(_('center longitude'))
    is_external = models.BooleanField()

class ZonePoint(models.Model):
    zone = models.ForeignKey(Zone, verbose_name=_('Zone'), db_index=True)
    lat = models.FloatField(_('latitude'))
    lng = models.FloatField(_('longitude'))
    
    class Meta:
        db_table = 'nodes_zone_point'

class ZoneExternal(Zone):
    owners = models.CharField(_('zone owners, eg: ninux, freifunk'), max_length=25)
    map = models.URLField(_('map URL'))
    api = models.URLField(_('API URL'))
    public_key = models.TextField(_('Public key'))
    email = models.EmailField(_('email'), blank=True, null=True)
    website = models.URLField(_('Website'), blank=True, null=True)
    
    class Meta:
        db_table = 'nodes_zone_external'

class Node(BaseAccessLevel):
    name = models.CharField(_('name'), max_length=50, unique=True)
    zone = models.ForeignKey(Zone, blank=True)
    latitude = models.FloatField(_('latitude'))
    longitude = models.FloatField(_('longitude')) 
    elevation = models.FloatField(_('elevation'), blank=True, null=True)
    status = models.SmallIntegerField(_('status'), max_length=3, choices=NODE_STATUS, default=1)
    user = models.ForeignKey(User, blank=True, null=True) # nodes might be assigned to a foreign zone
    hotspot = models.BooleanField(_('hotspot'), default=False)
    description = models.CharField(_('description'), max_length=255, blank=True, null=True)
    slug = models.SlugField(max_length=50, db_index=True, unique=True)
    notes = models.TextField(_('notes'), blank=True, null=True)

class Image(BaseOrdered):
    node = models.ForeignKey(Node, verbose_name=_('node'))
    file = models.ImageField(upload_to='/nodes/', verbose_name=_('image'))
    description = models.CharField(_('description'), max_length=255, blank=True, null=True)
    
    class Meta:
        db_table = 'nodes_node_image'