from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.base.models import BaseAccessLevel
from nodeshot.core.base.managers import AccessLevelManager

from . import Category
from .choices import SERVICE_STATUS


class Service(BaseAccessLevel):
    """
    Service Model
    Describes a service, eg: ftp, storage, proxy, ecc.
    """
    device = models.ForeignKey('net.Device', verbose_name=_('device'))
    name = models.CharField(_('name'), max_length=30)
    category = models.ForeignKey(Category, verbose_name=_('category') )
    description = models.TextField(_('description'), blank=True, null=True)
    documentation_url = models.URLField(_('documentation url'), blank=True, null=True)
    status = models.SmallIntegerField(_('status'), choices=SERVICE_STATUS)
    is_published = models.BooleanField(_('published'), default=True)
    
    objects = AccessLevelManager()
    
    class Meta:
        app_label = 'services'
        verbose_name = _('service')
        verbose_name_plural = _('services')
    
    def __unicode__(self):
        return '%s' % self.name