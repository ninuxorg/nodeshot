from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from nodeshot.core.base.models import BaseDate
from nodeshot.core.base.choices import TIME_ZONES, MAP_ZOOM

class Zone(BaseDate):
    name = models.CharField(_('name'), max_length=50, unique=True)
    parent = models.ForeignKey('Zone', blank=True, null=True)
    time_zone = models.CharField(_('time zone'), max_length=8, choices=TIME_ZONES, default=settings.NODESHOT['DEFAULTS']['ZONE_TIME'])
    description = models.CharField(_('description'), max_length=250, blank=True, null=True)
    slug = models.SlugField(max_length=50, db_index=True, unique=True)
    lat = models.FloatField(_('center latitude'))
    lng = models.FloatField(_('center longitude'))
    zoom = models.SmallIntegerField(_('default zoom level'), choices=MAP_ZOOM, default=settings.NODESHOT['DEFAULTS']['ZONE_ZOOM'])
    mantainers = models.CharField(_('mantainers'), help_text=_('Organizations like Ninux, Freifunk or people like Alice and Bob'), max_length=255)
    email = models.EmailField(_('email'), help_text=_('possibly an email address that delivers messages to all the active participants'))
    website = models.URLField(_('Website'), blank=True, null=True)
    is_external = models.BooleanField()
    
    class Meta:
        db_table = 'zones_zone'
        app_label= 'zones'
    
    def __unicode__(self):
        return '%s' % self.name
        
    if 'grappelli' in settings.INSTALLED_APPS:
        @staticmethod
        def autocomplete_search_fields():
            return ('name__icontains', 'slug__icontains')