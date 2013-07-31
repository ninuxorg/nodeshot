from django.db import models
from django.utils.translation import ugettext_lazy as _


class Status(models.Model):
    """
    Status of a node, eg: active, potential, approved
    """
    name = models.CharField(_('name'), max_length=255, help_text=_('label for this status, eg: active, approved, proposed'))
    slug = models.SlugField(max_length=75, db_index=True, unique=True)
    description = models.CharField(_('description'), max_length=255,
                                   help_text=_('this description will be used in the legend'))
    
    # order
    # is_default
    
    class Meta:
        db_table = 'nodes_status'
        app_label= 'nodes'
        verbose_name = _('status')
        verbose_name_plural = _('statuses')
    
    def __unicode__(self):
        return self.name
    