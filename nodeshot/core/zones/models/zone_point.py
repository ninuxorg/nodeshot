from django.db import models
from django.utils.translation import ugettext_lazy as _
from zone import Zone

class ZonePoint(models.Model):
    """
    Geographic points that delimit the perimeter of a 'Zone'
    """
    zone = models.ForeignKey(Zone, verbose_name=_('Zone'), db_index=True)
    lat = models.FloatField(_('latitude'))
    lng = models.FloatField(_('longitude'))
    
    class Meta:
        db_table = 'zones_zone_point'
        app_label= 'zones'