from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from nodeshot.core.base.models import BaseDate
from manufacturer import Manufacturer


class DeviceModel(BaseDate):
    """
    Device Type Model
    Eg.: Nanostation M5, Rocket M2, ecc.
    """
    manufacturer = models.ForeignKey(Manufacturer)
    name = models.CharField(_('name'), max_length=50, unique=True)
    image = models.ImageField(_('image'), upload_to='devices/images/', blank=True)
    datasheet = models.FileField(_('datasheet'), upload_to='devices/datasheets/', blank=True)
    cpu = models.CharField(_('CPU'), max_length=255, blank=True)
    ram = models.IntegerField(_('RAM'), blank=True, help_text=_('bytes'))
    
    class Meta:
        app_label= 'hardware'
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