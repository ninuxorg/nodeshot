from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class ImageMixin(models.Model):
    """
    Abstract model with few useful methods to display an image
    """
    
    image_width = 80
    
    class Meta:
        abstract = True
    
    def __unicode__(self, *args, **kwargs):
        return self.name
    
    def image_url(self):
        return '%s%s' % (settings.MEDIA_URL, self.image) 
    
    def image_img_tag(self):
        if self.image != '':
            return '<img src="%s" alt="" style="width:%spx" />' % (self.image_url(), self.image_width)
        else:
            return _('No image available')
    
    image_img_tag.allow_tags = True