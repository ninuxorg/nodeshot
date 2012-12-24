from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from nodeshot.core.base.models import BaseDate


class Manufacturer(BaseDate):
    """
    Manufacturer Model
    Eg: Ubiquiti, Mikrotic, Dlink, ecc.
    """
    name = models.CharField(_('name'), max_length=50, unique=True)
    url = models.URLField(_('url'))
    logo = models.ImageField(_('logo'), blank=True, upload_to='manufacturers/')
    
    class Meta:
        app_label= 'hardware'
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
        return '<img src="%s" alt="" style="width:250px" />' % self.logo_url() if self.image != '' else _('No image available')
    
    url_tag.allow_tags = True
    logo_img_tag.allow_tags = True