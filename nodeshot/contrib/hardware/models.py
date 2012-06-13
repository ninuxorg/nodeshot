from django.db import models
from django.utils.translation import ugettext_lazy as _
from nodeshot.core.base.models import BaseDate, BaseAccessLevel
from nodeshot.core.network.models import Device, Interface
from nodeshot.core.base.choices import POLARIZATIONS

class Manufacturer(BaseDate):
    name = models.CharField(_('name'), max_length=50)
    url = models.URLField(_('url'))

class DeviceModel(BaseDate):
    name = models.CharField(_('name'), max_length=50, unique=True)
    manufacturer = models.ForeignKey(Manufacturer)
    image = models.ImageField(_('image'), upload_to='devices/images/', blank=True, null=True)
    manual = models.FileField(_('manual'), upload_to='devices/manuals/', blank=True, null=True)
    mac_prefix = models.CharField(_('mac address prefix'), max_length=17, blank=True, null=True)
    
    class Meta:
        db_table = 'hardware_device_model'

class Devicel2Model(models.Model):
    device = models.OneToOneField(Device, verbose_name=_('device'))

class AntennaModel(BaseDate):
    name = models.CharField(_('name'), max_length=50, unique=True)
    manufacturer = models.ForeignKey(Manufacturer)
    gain = models.FloatField(_('gain'))
    freq_range_lower = models.FloatField(_('Minimum Frequency'))
    freq_range_higher = models.FloatField(_('Maximum Frequency'))
    beamwidth_h = models.IntegerField(_('Hpol Beamwidth'))
    beamwidth_v = models.IntegerField(_('Vpol Beamwidth'))
    image = models.ImageField(_('image'), upload_to='devices/images/', blank=True, null=True)
    specification = models.URLField(_('specification'), blank=True, null=True)
    
    class Meta:
        db_table = 'hardware_antenna_model'

class Antenna(BaseDate):
    radio = models.ForeignKey(Interface)
    model = models.ForeignKey(AntennaModel)
    polarization = models.CharField(_('Polarization'), max_length='20', choices=POLARIZATIONS)
    azimuth = models.FloatField(_('azimuth'))
    elevation = models.FloatField(_('elevation'))
    inclination = models.FloatField(_('inclination'), blank=True, null=True)

class RadiationPattern(BaseDate):
    antenna_model = models.ForeignKey(AntennaModel)
    type = models.CharField(_('type'), max_length=30)
    image = models.ImageField(upload_to='radiation_patterns/', verbose_name=_('image'))
    
    class Meta:
        db_table = 'hardware_radiation_pattern'