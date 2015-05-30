from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.base.models import BaseDate
from . import ImageMixin


class Manufacturer(BaseDate, ImageMixin):
    """
    Manufacturer Model
    Eg: Ubiquiti, Mikrotic, Dlink, ecc.
    """
    name = models.CharField(_('name'), max_length=50, unique=True)
    url = models.URLField(_('url'), blank=True)
    image = models.ImageField(_('logo'), blank=True, upload_to='manufacturers/')
    image_width = 180
    
    class Meta:
        app_label= 'hardware'
        verbose_name = _('Manufacturer')
        verbose_name_plural = _('Manufacturers')
        ordering = ['name']
    
    def __unicode__(self):
        return self.name
    
    def url_tag(self):
        return '<a href="%s" target="_blank">%s</a>' % (self.url, self.url)
        
    url_tag.allow_tags = True
