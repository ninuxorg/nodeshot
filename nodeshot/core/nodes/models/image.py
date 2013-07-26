import os

from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.base.models import BaseOrdered
from nodeshot.core.base.managers import AccessLevelManager

from . import Node


class Image(BaseOrdered):
    """
    Images of a 'Node'
    """
    node = models.ForeignKey(Node, verbose_name=_('node'))
    file = models.ImageField(upload_to='nodes/', verbose_name=_('image'))
    description = models.CharField(_('description'), max_length=255, blank=True, null=True)
    
    # manager
    objects = AccessLevelManager()
    
    class Meta:
        db_table = 'nodes_image'
        app_label= 'nodes'
        permissions = (('can_view_image', 'Can view images'),)
        ordering = ['order']
    
    def __unicode__(self):
        return self.file.name
    
    def delete(self, *args, **kwargs):
        """ delete image when an image record is deleted """
        try:
            os.remove(self.file.file.name)
        # image does not exist
        except (OSError, IOError):
            pass
        
        super(Image, self).delete(*args, **kwargs)
    