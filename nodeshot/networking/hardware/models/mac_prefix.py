from django.db import models
from django.utils.translation import ugettext_lazy as _

from . import Manufacturer


class MacPrefix(models.Model):
    """ Mac prefix of a Manufacturer """
    manufacturer = models.ForeignKey(Manufacturer, verbose_name=_('manufacturer'))
    prefix = models.CharField(_('mac address prefix'), max_length=8, unique=True)
    
    def __unicode__(self):
        return self.prefix
    
    class Meta:
        app_label= 'hardware'
        verbose_name = _('MAC Prefix')
        verbose_name_plural = _('MAC Prefixes')
