from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from nodeshot.core.base.models import BaseDate
from nodeshot.core.base.choices import TIME_ZONES, MAP_ZOOM
from nodeshot.core.zones.managers import ZoneManager

class Zone(BaseDate):
    name = models.CharField(_('name'), max_length=50, unique=True)
    is_published = models.BooleanField(_('published'), default=True)
    is_external = models.BooleanField(_('is it external?'))
    parent = models.ForeignKey('Zone', blank=True, null=True)
    time_zone = models.CharField(_('time zone'), max_length=8, choices=TIME_ZONES, default=settings.NODESHOT['DEFAULTS']['ZONE_TIME'])
    description = models.CharField(_('description'), max_length=250, blank=True, null=True)
    slug = models.SlugField(max_length=50, db_index=True, unique=True)
    lat = models.FloatField(_('center latitude'))
    lng = models.FloatField(_('center longitude'))
    zoom = models.SmallIntegerField(_('default zoom level'), choices=MAP_ZOOM, default=settings.NODESHOT['DEFAULTS']['ZONE_ZOOM'])
    organization = models.CharField(_('organization'), help_text=_('eg: Ninux, Freifunk, Alice, Bob, etc.'), max_length=255)
    website = models.URLField(_('Website'), blank=True, null=True)
    email = models.EmailField(_('email'), help_text=_('possibly an email address that delivers messages to all the active participants; if you don\'t have such an email you can add specific users in the "mantainers" field'), blank=True)
    mantainers = models.ManyToManyField(User, verbose_name=_('mantainers'), help_text=_('you can specify the users who are mantaining this zone so they will receive emails from the system'), blank=True)
    #points = models.CharField
    
    objects = ZoneManager()
    
    class Meta:
        db_table = 'zones_zone'
        app_label= 'zones'
    
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
        
        if self.is_external and self.parent:
            raise ValidationError(_('External zones cannot have parents'))
        
        if self.parent and self.parent.is_external:
            raise ValidationError(_('Zones cannot have parents flagged as "external"'))
        
        #if not self.email and not self.mantainers:
        #    raise ValidationError(_('Either an email or some mantainers should be set'))