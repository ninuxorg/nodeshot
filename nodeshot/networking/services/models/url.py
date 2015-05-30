from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.base.models import BaseDate
from choices import APPLICATION_PROTOCOLS, TRANSPORT_PROTOCOLS


class Url(BaseDate):
    service = models.ForeignKey('services.Service',
                                verbose_name=_('service'))
    transport = models.CharField(_('transport protocol'), max_length=5,
                                 choices=TRANSPORT_PROTOCOLS,
                                 default=TRANSPORT_PROTOCOLS[1][0])
    application = models.CharField(_('application protocol'), max_length=20,
                                   choices=APPLICATION_PROTOCOLS)
    ip = models.ForeignKey('net.Ip', verbose_name=_('ip address'))
    port = models.IntegerField(_('port'), blank=True, null=True)
    path = models.CharField(_('path'), max_length=50, blank=True)
    domain = models.CharField(_('domain'), max_length=50, blank=True)
    
    class Meta:
        app_label= 'services'
        db_table = 'service_urls'
        verbose_name = _('url')
        verbose_name_plural = _('urls')
    
    def __unicode__(self):
        value = ''
        if self.application:
            value = '%s://' % self.application
        if self.domain:
            value += self.domain
        else:
            if self.ip.protocol == 'ipv4':
                encaps = '%s'
            else:
                encaps = '[%s]'
            value += encaps % self.ip.address
        if self.port:
            value += ':%s' % self.port
        return value
