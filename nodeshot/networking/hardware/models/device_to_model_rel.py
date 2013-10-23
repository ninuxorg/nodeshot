from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodeshot.networking.net.models import Device
from . import DeviceModel, Antenna, AntennaModel


class DeviceToModelRel(models.Model):
    """ OneToOne relationship between net.Device and hardware.DeviceModel """
    device = models.OneToOneField(Device, verbose_name=_('device'), related_name='hardware')
    model = models.ForeignKey(DeviceModel)
    cpu = models.CharField(_('CPU'), max_length=255, blank=True)
    ram = models.IntegerField(_('RAM'), blank=True, help_text=_('bytes'))
    
    class Meta:
        app_label= 'hardware'
        db_table = 'hardware_device_to_model'
        verbose_name = _('Device Model Information')
        verbose_name_plural = _('Device Model Information')
    
    def __unicode__(self):
        return '%s (%s)' % (self.device.name, self.model.name)
    
    def save(self, *args, **kwargs):
        """ when creating a new record fill CPU and RAM info if available """
        adding_new = False
        if not self.pk or (not self.cpu and not self.ram):
            # if self.model.cpu is not empty
            if self.model.cpu:
                self.cpu = self.model.cpu
            # if self.model.ram is not empty
            if self.model.ram:
                self.ram = self.model.ram
            # mark to add a new antenna
            adding_new = True
        # perform save
        super(DeviceToModelRel, self).save(*args, **kwargs)
        # after Device2Model object has been saved
        try:
            # does the device model have an integrated antenna?
            antenna_model = self.model.antennamodel
        except AntennaModel.DoesNotExist:
            # if not antenna_model is False
            antenna_model = False
        # if we are adding a new device2model and the device model has an integrated antenna
        if adding_new and antenna_model:
            # create new Antenna object
            antenna = Antenna(
                device=self.device,
                model=self.model.antennamodel
            )
            # retrieve wireless interfaces and assign it to the antenna object if possible
            wireless_interfaces = self.device.interface_set.filter(type=2)
            if len(wireless_interfaces) > 0:
                antenna.radio = wireless_interfaces[0]
            # save antenna
            antenna.save()
