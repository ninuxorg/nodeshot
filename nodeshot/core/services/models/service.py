from django.db import models
from django.utils.translation import ugettext_lazy as _
from nodeshot.core.base.models import BaseAccessLevel
from nodeshot.core.base.choices import SERVICE_STATUS
from category import Category

class Service(BaseAccessLevel):
    device = models.ForeignKey('network.Device', verbose_name=_('device'))
    name = models.CharField(_('name'), max_length=30)
    category = models.ForeignKey(Category, verbose_name=_('category') )
    description = models.TextField(_('description'), blank=True, null=True)
    documentation_url = models.URLField(_('documentation url'), blank=True, null=True)
    status = models.SmallIntegerField(_('status'), choices=SERVICE_STATUS)
    is_published = models.BooleanField(_('published'), default=True)
    
    class Meta:
        permissions = (('can_view_services', 'Can view services'),)
        verbose_name = _('service')
        verbose_name_plural = _('services')
        app_label = 'services'
    
    def __unicode__(self):
        return '%s' % self.name