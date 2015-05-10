from netfields import InetAddressField, CidrAddressField

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from nodeshot.core.base.models import BaseAccessLevel
from ..managers import NetAccessLevelManager
from choices import IP_PROTOCOLS



class Ip(BaseAccessLevel):
    """ IP Address Model """
    interface = models.ForeignKey('net.Interface', verbose_name=_('interface'))
    address = InetAddressField(verbose_name=_('ip address'), unique=True, db_index=True)
    protocol = models.CharField(_('IP Protocol Version'), max_length=4, choices=IP_PROTOCOLS, default=IP_PROTOCOLS[0][0], blank=True)
    netmask = CidrAddressField(_('netmask (CIDR, eg: 10.40.0.0/24)'), blank=True, null=True)

    objects = NetAccessLevelManager()

    class Meta:
        app_label = 'net'
        permissions = (('can_view_ip', 'Can view ip'),)
        verbose_name = _('ip address')
        verbose_name_plural = _('ip addresses')

    def __unicode__(self):
        return '%s: %s' % (self.protocol, self.address)

    def clean(self, *args, **kwargs):
        """ TODO """
        # netaddr.IPAddress('10.40.2.1') in netaddr.IPNetwork('10.40.0.0/24')
        pass

    def save(self, *args, **kwargs):
        """
        Determines ip protocol version automatically.
        Stores address in interface shortcuts for convenience.
        """
        self.protocol = 'ipv%d' % self.address.version
        # save
        super(Ip, self).save(*args, **kwargs)

        # TODO: do we really need this?
        # save shortcut on interfaces
        #ip_cached_list = self.interface.ip_addresses
        ## if not present in interface shorctus add it to the list
        #if str(self.address) not in ip_cached_list:
        #    # recalculate cached_ip_list
        #    recalculated_ip_cached_list = []
        #    for ip in self.interface.ip_set.all():
        #        recalculated_ip_cached_list.append(str(ip.address))
        #    # rebuild string in format "<ip_1>, <ip_2>"
        #    self.interface.data['ip_addresses'] = recalculated_ip_cached_list
        #    self.interface.save()

    @property
    def owner(self):
        return self.interface.owner

    if 'grappelli' in settings.INSTALLED_APPS:
        @staticmethod
        def autocomplete_search_fields():
            return ('address__icontains',)
