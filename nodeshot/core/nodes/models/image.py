from django.db import models
from django.utils.translation import ugettext_lazy as _
from nodeshot.core.base.models import BaseOrdered
from node import Node

class Image(BaseOrdered):
    """
    Images of a 'Node'
    """
    node = models.ForeignKey(Node, verbose_name=_('node'))
    file = models.ImageField(upload_to='nodes/', verbose_name=_('image'))
    description = models.CharField(_('description'), max_length=255, blank=True, null=True)
    
    class Meta:
        db_table = 'nodes_image'
        app_label= 'nodes'
        permissions = (('can_view_image', 'Can view images'),)
        ordering = ['order']