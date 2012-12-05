from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from nodeshot.core.base.models import BaseAccessLevel
from nodeshot.core.base.choices import IP_PROTOCOLS

class Ip(BaseAccessLevel):
    interface = models.ForeignKey('network.Interface', verbose_name=_('interface'))
    address = models.GenericIPAddressField(verbose_name=_('ip address'), unique=True)
    protocol = models.CharField(_('IP Protocol Version'), max_length=4, choices=IP_PROTOCOLS, default=IP_PROTOCOLS[0][0], blank=True)
    netmask = models.CharField(_('netmask / prefix'), max_length=100)
    
    class Meta:
        app_label= 'network'
        permissions = (('can_view_ip', 'Can view ip'),)
        verbose_name = _('ip address')
        verbose_name_plural = _('ip addresses')
    
    def __unicode__(self):
        return '%s: %s' % (self.protocol, self.address)
    
    def save(self, *args, **kwargs):
        """ Determines ip protocol version automatically """
        if '.' in self.address:
            self.protocol = 'ipv4'
        elif ':' in self.address:
            self.protocol = 'ipv6'
        # save
        super(Ip, self).save(*args, **kwargs)
    
    if 'grappelli' in settings.INSTALLED_APPS:
        @staticmethod
        def autocomplete_search_fields():
            return ('address__icontains',)