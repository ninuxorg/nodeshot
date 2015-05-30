from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.base.models import BaseDate


class Category(BaseDate):
    """
    Categories of services
    """
    name = models.CharField(_('name'), max_length=30)
    description = models.TextField(_('description'), blank=True, null=True)
    
    class Meta:
        app_label = 'services'
        db_table = 'service_category'
        verbose_name = _('category')
        verbose_name_plural = _('categories')
    
    def __unicode__(self):
        return '%s' % self.name