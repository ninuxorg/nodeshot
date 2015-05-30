import os

from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.base.models import BaseOrderedACL
from nodeshot.core.base.managers import AccessLevelManager


class Image(BaseOrderedACL):
    """
    Images of a 'Node'
    """
    node = models.ForeignKey('nodes.Node', verbose_name=_('node'))
    file = models.ImageField(upload_to='nodes/', verbose_name=_('image'))
    description = models.CharField(_('description'), max_length=255, blank=True, null=True)

    # manager
    objects = AccessLevelManager()

    class Meta:
        db_table = 'nodes_image'
        app_label = 'nodes'
        permissions = (('can_view_image', 'Can view images'),)
        ordering = ['order']

    def __unicode__(self):
        return self.file.name

    def get_auto_order_queryset(self):
        """ overriding a BaseOrdered Abstract Model method """
        return self.__class__.objects.filter(node=self.node)

    def delete(self, *args, **kwargs):
        """ delete image when an image record is deleted """
        try:
            os.remove(self.file.file.name)
        # image does not exist
        except (OSError, IOError):
            pass

        super(Image, self).delete(*args, **kwargs)
