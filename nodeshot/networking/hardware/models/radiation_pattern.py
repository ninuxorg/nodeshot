from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.base.models import BaseDate
from . import ImageMixin, AntennaModel


class RadiationPattern(BaseDate, ImageMixin):
    """ Radiation Pattern of an Antenna Model """
    antenna_model = models.ForeignKey(AntennaModel)
    type = models.CharField(_('type'), max_length=30)
    image = models.ImageField(upload_to='antennas/radiation_patterns/', verbose_name=_('image'))
    
    def __unicode__(self):
        return _('radiation pattern for antenna model: %s' % self.antenna_model)
    
    class Meta:
        app_label= 'hardware'
        db_table = 'hardware_radiation_pattern'
