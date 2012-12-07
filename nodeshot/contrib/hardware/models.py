from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from nodeshot.core.base.models import BaseDate, BaseAccessLevel
from nodeshot.core.network.models import Device, Interface
from nodeshot.core.base.choices import POLARIZATIONS

class Manufacturer(BaseDate):    
    name = models.CharField(_('name'), max_length=50, unique=True)
    url = models.URLField(_('url'))
    logo = models.ImageField(_('logo'), blank=True, upload_to='manufacturers/')
    
    class Meta:
        verbose_name = _('Manufacturer')
        verbose_name_plural = _('Manufacturers')
        ordering = ['name']
    
    def __unicode__(self, *args, **kwargs):
        return self.name
    
    def url_tag(self):
        return '<a href="%s" target="_blank">%s</a>' % (self.url, self.url)
    
    def logo_url(self):
        return '%s%s' % (settings.MEDIA_URL, self.logo) 
    
    def logo_img_tag(self):
        return '<img src="%s" alt="" style="width:250px" />' % self.logo_url()
    
    url_tag.allow_tags = True
    logo_img_tag.allow_tags = True

class MacPrefix(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, verbose_name=_('manufacturer'))
    prefix = models.CharField(_('mac address prefix'), max_length=8, unique=True)
    
    class Meta:
        verbose_name = _('MAC Prefix')
        verbose_name_plural = _('MAC Prefixes')

class DeviceModel(BaseDate):
    manufacturer = models.ForeignKey(Manufacturer)
    name = models.CharField(_('name'), max_length=50, unique=True)
    image = models.ImageField(_('image'), upload_to='devices/images/', blank=True)
    datasheet = models.FileField(_('datasheet'), upload_to='devices/datasheets/', blank=True)
    cpu = models.CharField(_('CPU'), max_length=255, blank=True)
    ram = models.IntegerField(_('RAM'), blank=True)
    
    class Meta:
        db_table = 'hardware_device_model'
        verbose_name = _('Device Model')
        verbose_name_plural = _('Device Models')
    
    def __unicode__(self, *args, **kwargs):
        return self.name
    
    def image_url(self):
        return '%s%s' % (settings.MEDIA_URL, self.image) 
    
    def image_img_tag(self):
        return '<img src="%s" alt="" style="width:80px" />' % self.image_url()
    
    image_img_tag.allow_tags = True

class Device2Model(models.Model):
    device = models.OneToOneField(Device, verbose_name=_('device'))
    model = models.ForeignKey(DeviceModel)
    cpu = models.CharField(_('CPU'), max_length=255, blank=True)
    ram = models.IntegerField(_('RAM'), blank=True)
    
    class Meta:
        verbose_name = _('Device Model Information')
        verbose_name_plural = _('Device Model Information')
    
    def __unicode__(self):
        return '%s (%s)' % (self.device.name, self.model.name)
    
    def save(self, *args, **kwargs):
        """ when creating a new record fill CPU and RAM info if available """
        if not self.id or (not self.cpu and not self.ram):
            # if self.model.cpu is not empty
            if self.model.cpu:
                self.cpu = self.model.cpu
            # if self.model.ram is not empty
            if self.model.ram:
                self.ram = self.model.ram
            
        super(Device2Model, self).save(*args, **kwargs)

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
    model = models.ForeignKey(AntennaModel)
    radio = models.ForeignKey(Interface)    
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