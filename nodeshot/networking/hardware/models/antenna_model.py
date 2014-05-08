from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.base.models import BaseDate
from choices import POLARIZATION_CHOICES

from . import ImageMixin, DeviceModel, Manufacturer


class AntennaModel(BaseDate, ImageMixin):
    """
    Antenna Type Model
    Eg: Airmax Sector, Rocket Dish, ecc.
    """
    name = models.CharField(_('name'), max_length=50, unique=True)
    device_model = models.OneToOneField(DeviceModel, blank=True, null=True, help_text=_('specify only if it\'s an integrated antenna'))
    manufacturer = models.ForeignKey(Manufacturer)
    gain = models.DecimalField(_('gain'), max_digits=4, decimal_places=1, help_text=_('dBi'))
    polarization = models.SmallIntegerField(_('Polarization'), choices=POLARIZATION_CHOICES, blank=True, null=True)
    freq_range_lower = models.IntegerField(_('minimum Frequency'), help_text=_('MHz'))
    freq_range_higher = models.IntegerField(_('maximum Frequency'), help_text=_('MHz'))
    beamwidth_h = models.DecimalField(_('hpol Beamwidth'), max_digits=4, decimal_places=1, help_text=_('degrees'))
    beamwidth_v = models.DecimalField(_('vpol Beamwidth'), max_digits=4, decimal_places=1, help_text=_('degrees'))
    image = models.ImageField(_('image'), upload_to='antennas/images/', blank=True)
    datasheet = models.FileField(_('datasheet'), upload_to='antennas/datasheets/', blank=True)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        app_label= 'hardware'
        db_table = 'hardware_antenna_model'
