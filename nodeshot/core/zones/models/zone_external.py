from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from zone import Zone

class ZoneExternal(models.Model):
    """
    External Zones, extend 'Zones' with additional files
    These are the zones that are managed by local groups or other communities
    """
    #owners = models.CharField(_('zone owners, eg: ninux, freifunk'), max_length=25)
    zone = models.OneToOneField(Zone, verbose_name=_('zone'), parent_link=True, related_name='external')
    map = models.URLField(_('map URL'))
    api = models.URLField(_('API URL'))
    #public_key = models.TextField(_('Public key'))
    
    class Meta:
        db_table = 'zones_external'
        app_label= 'zones'
        verbose_name = _('external zone info')
        verbose_name_plural = _('external zones info')
