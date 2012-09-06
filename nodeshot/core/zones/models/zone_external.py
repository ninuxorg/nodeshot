from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from zone import Zone

class ZoneExternal(Zone):
    """
    External Zones, extend 'Zones' with additional files
    These are the zones that are managed by local groups or other communities
    """
    owners = models.CharField(_('zone owners, eg: ninux, freifunk'), max_length=25)
    map = models.URLField(_('map URL'))
    api = models.URLField(_('API URL'))
    public_key = models.TextField(_('Public key'))
    email = models.EmailField(_('email'), blank=True, null=True)
    website = models.URLField(_('Website'), blank=True, null=True)
    
    class Meta:
        db_table = 'zones_zone_external'
        app_label= 'zones'
        verbose_name = _('external zone')
        verbose_name_plural = _('external zones')
