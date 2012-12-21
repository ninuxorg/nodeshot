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
    ram = models.IntegerField(_('RAM'), blank=True, help_text=_('bytes'))
    
    class Meta:
        db_table = 'hardware_device_model'
        verbose_name = _('Device Model')
        verbose_name_plural = _('Device Models')
    
    def __unicode__(self, *args, **kwargs):
        return self.name
    
    def image_url(self):
        return '%s%s' % (settings.MEDIA_URL, self.image) 
    
    def image_img_tag(self):
        return '<img src="%s" alt="" style="width:80px" />' % self.image_url() if self.image != '' else _('No image available')
    
    image_img_tag.allow_tags = True

class Device2Model(models.Model):
    device = models.OneToOneField(Device, verbose_name=_('device'))
    model = models.ForeignKey(DeviceModel)
    cpu = models.CharField(_('CPU'), max_length=255, blank=True)
    ram = models.IntegerField(_('RAM'), blank=True, help_text=_('bytes'))
    
    class Meta:
        verbose_name = _('Device Model Information')
        verbose_name_plural = _('Device Model Information')
    
    def __unicode__(self):
        return '%s (%s)' % (self.device.name, self.model.name)
    
    def save(self, *args, **kwargs):
        """ when creating a new record fill CPU and RAM info if available """
        add_new_antenna = False
        if not self.pk or (not self.cpu and not self.ram):
            # if self.model.cpu is not empty
            if self.model.cpu:
                self.cpu = self.model.cpu
            # if self.model.ram is not empty
            if self.model.ram:
                self.ram = self.model.ram
            # mark to add a new antenna
            add_new_antenna = True
        # perform save
        super(Device2Model, self).save(*args, **kwargs)
        # after save
        # if this model has an integrated antenna automatically add an antenna to the device
        if add_new_antenna and self.model.antennamodel:
            # create new Antenna object
            antenna = Antenna(
                device=self.device,
                model=self.model.antennamodel
            )
            # retrieve wireless interfaces and assign it to the antenna object if possible
            wireless_interfaces = self.device.interface_set.filter(type=2)
            if len(wireless_interfaces) > 0:
                antenna.radio = wireless_interfaces[0]
            # save
            antenna.save()

class AntennaModel(BaseDate):
    name = models.CharField(_('name'), max_length=50, unique=True)
    device_model = models.OneToOneField(DeviceModel, blank=True, null=True, help_text=_('specify only if it\'s an integrated antenna'))
    manufacturer = models.ForeignKey(Manufacturer)
    gain = models.DecimalField(_('gain'), max_digits=4, decimal_places=1, help_text=_('dBi'))
    freq_range_lower = models.IntegerField(_('minimum Frequency'), help_text=_('MHz'))
    freq_range_higher = models.IntegerField(_('maximum Frequency'), help_text=_('MHz'))
    beamwidth_h = models.DecimalField(_('hpol Beamwidth'), max_digits=4, decimal_places=1, help_text=_('degrees'))
    beamwidth_v = models.DecimalField(_('vpol Beamwidth'), max_digits=4, decimal_places=1, help_text=_('degrees'))
    image = models.ImageField(_('image'), upload_to='antennas/images/', blank=True)
    datasheet = models.FileField(_('datasheet'), upload_to='antennas/datasheets/', blank=True)
    
    class Meta:
        db_table = 'hardware_antenna_model'
    
    def __unicode__(self, *args, **kwargs):
        return self.name
    
    def image_url(self):
        return '%s%s' % (settings.MEDIA_URL, self.image) 
    
    def image_img_tag(self):
        return '<img src="%s" alt="" style="width:80px" />' % self.image_url() if self.image != '' else _('No image available')
    
    image_img_tag.allow_tags = True

class Antenna(BaseDate):
    # device is redundant but it allows us to manage it easily in the django admin
    device = models.ForeignKey(Device)
    model = models.ForeignKey(AntennaModel)
    radio = models.ForeignKey(Interface, blank=True, null=True) #TODO: this should not be blank nor null    
    polarization = models.CharField(_('Polarization'), max_length='20', choices=POLARIZATIONS, blank=True)
    azimuth = models.FloatField(_('azimuth'), blank=True, null=True)
    elevation = models.FloatField(_('elevation'), blank=True, null=True)
    inclination = models.FloatField(_('inclination'), blank=True, null=True)

class RadiationPattern(BaseDate):
    antenna_model = models.ForeignKey(AntennaModel)
    type = models.CharField(_('type'), max_length=30)
    image = models.ImageField(upload_to='antennas/radiation_patterns/', verbose_name=_('image'))
    
    class Meta:
        db_table = 'hardware_radiation_pattern'