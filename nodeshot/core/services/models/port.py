from django.db import models
from django.utils.translation import ugettext_lazy as _
from nodeshot.core.base.models import BaseDate
from nodeshot.core.base.choices import PORT_PROTOCOLS

class Port(BaseDate):
    service = models.ForeignKey('services.Service', verbose_name=_('service'))
    port = models.IntegerField(_('port'))
    protocol = models.CharField(_('protocol'), max_length=5, choices=PORT_PROTOCOLS, default=PORT_PROTOCOLS[1][0])
    description = models.CharField(_('description'), max_length=255, blank=True)
    
    class Meta:
        db_table = 'services_service_port'
        app_label = 'services'
        verbose_name = _('port')
        verbose_name_plural = _('ports')
    
    def __unicode__(self):
        return '%s' % self.port 