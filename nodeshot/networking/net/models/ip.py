from django.db import models, DatabaseError, IntegrityError
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from nodeshot.core.base.models import BaseAccessLevel
from choices import IP_PROTOCOLS

from netfields import InetAddressField, CidrAddressField, NetManager


class Ip(BaseAccessLevel):
    """ IP Address Model """
    interface = models.ForeignKey('net.Interface', verbose_name=_('interface'))
    address = InetAddressField(verbose_name=_('ip address'), unique=True, db_index=True)
    protocol = models.CharField(_('IP Protocol Version'), max_length=4, choices=IP_PROTOCOLS, default=IP_PROTOCOLS[0][0], blank=True)
    netmask = CidrAddressField(_('netmask (CIDR, eg: 10.40.0.0/24)'))
    
    objects = NetManager()
    
    class Meta:
        app_label= 'net'
        permissions = (('can_view_ip', 'Can view ip'),)
        verbose_name = _('ip address')
        verbose_name_plural = _('ip addresses')
    
    def __unicode__(self):
        return '%s: %s' % (self.protocol, self.address)
    
    def full_clean(self, *args, **kwargs):
        """ TODO """
        pass
    
    def save(self, *args, **kwargs):
        """ Determines ip protocol version automatically """
        self.protocol = 'ipv%d' % self.address.version
        # save
        super(Ip, self).save(*args, **kwargs)
    
    if 'grappelli' in settings.INSTALLED_APPS:
        @staticmethod
        def autocomplete_search_fields():
            return ('address__icontains',)