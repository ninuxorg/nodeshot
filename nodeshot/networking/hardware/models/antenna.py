from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.base.models import BaseDate
from nodeshot.networking.net.models import Device, Interface

from choices import POLARIZATION_CHOICES
from . import AntennaModel


class Antenna(BaseDate):
    """ Antenna of a device. A device may have more than one antenna """
    # device foreign key is redundant but it allows us to manage it easily in the django admin
    device = models.ForeignKey(Device)
    model = models.ForeignKey(AntennaModel)
    radio = models.ForeignKey(Interface, blank=True, null=True) #TODO: this should not be blank nor null
    polarization = models.SmallIntegerField(_('Polarization'), choices=POLARIZATION_CHOICES, blank=True, null=True)
    azimuth = models.FloatField(_('azimuth'), blank=True, null=True)
    inclination = models.FloatField(_('inclination'), blank=True, null=True)
    
    # TODO: this must become a postgis point
    # elevation = models.FloatField(_('elevation'), blank=True, null=True)
    # lat = models.FloatField(_('latitude'), blank=True, null=True, help_text=_('automatically inherits the value of the node, specify a different value if needed'))
    # lng = models.FloatField(_('longitude'), blank=True, null=True, help_text=_('automatically inherits the value of the node, specify a different value if needed'))
    
    class Meta:
        app_label = 'hardware'
    
    def __unicode__(self):
        return self.model.__unicode__()
    
    def save(self, *args, **kwargs):
        """
        1. set polarization according to AntennaModel (self.model.polarization) when creating a new antenna
        2. inherit latitude and longitude from node
        """
        if not self.pk and self.model.polarization:
            self.polarization = self.model.polarization
        super(Antenna, self).save(*args, **kwargs)
