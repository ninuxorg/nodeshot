# -*- coding: utf-8 -*-
"""
this app can import data from older nodeshot versions (0.9)
developed to import data from map.ninux.org into the new version of nodeshot
"""

from nodeshot.core.base.utils import check_dependencies

check_dependencies(
    dependencies=[
        'nodeshot.core.nodes',
        'nodeshot.core.layers',
        'nodeshot.networking.net',
        'nodeshot.networking.links',
        'nodeshot.community.mailing',
        'nodeshot.community.profiles',
    ],
    module='nodeshot.interop.oldimporter'
)

from django.db import models
from django.utils.translation import ugettext_lazy as _

from .choices import *


__all__ = [
    'OldNode',
    'OldDevice',
    'OldHna',
    'OldInterface',
    'OldLink',
    'OldStatistic',
    'OldContact',
    'OldUser'
]


class OldNode(models.Model):
    name = models.CharField(_('name'), max_length=50, unique=True)
    slug = models.SlugField(max_length=50, db_index=True, unique=True)
    owner = models.CharField(_('owner'), max_length=50, blank=True, null=True)
    description = models.CharField(_('description'), max_length=200, blank=True, null=True)
    postal_code = models.CharField(_('postal code'), max_length=10, blank=True)
    email = models.EmailField()
    email2 = models.EmailField(blank=True, null=True)
    email3 = models.EmailField(blank=True, null=True)
    password =  models.CharField(max_length=255, help_text=_('Use "[algo]$[salt]$[hexdigest]" or use the  <a href="password/">change password form</a>.'))
    lat = models.FloatField(_('latitude'))
    lng = models.FloatField(_('longitude'))
    alt = models.FloatField(_('altitude'), blank=True, null=True)
    status = models.CharField(_('status'), max_length=3, choices=NODE_STATUS, default='p')
    activation_key = models.CharField(_('activation key'), max_length=40, blank=True, null=True, help_text=_('Key needed for activation of the node. It\'s deleted once the node is activated.'))
    notes = models.TextField(_('notes'), blank=True, null=True)
    added = models.DateTimeField(_('added on'), auto_now_add=True)
    updated = models.DateTimeField(_('updated on'), auto_now=True)

    def get_lat(self):
        """ returns latitude as string (avoid django converting the dot . into a comma , in certain language sets) """
        return str(self.lat)

    def get_lng(self):
        """ returns longitude as string (avoid django converting the dot . into a comma , in certain language sets) """
        return str(self.lng)

    def __unicode__(self):
        return u'%s' % (self.name)

    class Meta:
        verbose_name = _('Node')
        verbose_name_plural = _('Nodes')
        db_table = 'nodeshot_node'


class OldDevice(models.Model):
    name = models.CharField(_('name'), max_length=50, unique=True)
    cname = models.SlugField(_('CNAME'), help_text=_('Name used for DNS resolution. Example: grid1 becomes grid1.nodename.domain.org. If left empty device name is used as default.'), max_length=30, blank=True, null=True)
    description = models.CharField(_('description'), max_length=255, blank=True, null=True)
    type = models.CharField(_('type'), max_length=50, blank=True, null=True)
    node = models.ForeignKey(OldNode, verbose_name=_('node'))
    routing_protocol = models.CharField(_('routing protocol'), max_length=20, choices=ROUTING_PROTOCOLS, default=DEFAULT_ROUTING_PROTOCOL)
    routing_protocol_version = models.CharField(_('routing protocol version'), max_length=10, blank=True, null=True)
    added = models.DateTimeField(_('added on'), auto_now_add=True)
    updated = models.DateTimeField(_('updated on'), auto_now=True)

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = (('node', 'cname'),)
        verbose_name = _('OldDevice')
        verbose_name_plural = _('OldDevices')
        db_table = 'nodeshot_device'


class OldHna(models.Model):
    device = models.ForeignKey(OldDevice)
    route = models.CharField(max_length=43)

    def __unicode__(self):
        return u'%s' % (self.route)

    class Meta:
        verbose_name = _('Hna')
        verbose_name_plural = _('Hna')
        db_table = 'nodeshot_hna'


class OldInterface(models.Model):
    ipv4_address = models.IPAddressField(verbose_name=_('ipv4 address'), blank=True, null=True, unique=True, default=None)
    ipv6_address = models.GenericIPAddressField(protocol='IPv6', verbose_name=_('ipv6 address'), blank=True, null=True, unique=True, default=None)
    mac_address = models.CharField(max_length=17, blank=True, null=True, unique=True, default=None)
    type = models.CharField(max_length=10, choices=INTERFACE_TYPE)
    cname = models.SlugField(_('cname'), help_text=_('Name used for DNS resolution. Example: eth0 becomes eth0.devicecname.nodename.domain.org. If left empty the interface type is used as default.'), max_length=30, blank=True, null=True)
    device = models.ForeignKey(OldDevice)
    draw_link = models.BooleanField(_('Draw links'), help_text=_('Draw links from/to this interface (not valid for VPN interfaces)'), default=True, blank=True)
    wireless_mode = models.CharField(max_length=5, choices=WIRELESS_MODE, blank=True, null=True)
    wireless_channel = models.CharField(max_length=4, choices=WIRELESS_CHANNEL, blank=True, null=True)
    wireless_polarity = models.CharField(max_length=1, choices=WIRELESS_POLARITY, blank=True, null=True)
    essid = models.CharField(max_length=50, null=True, blank=True, default=None)
    bssid = models.CharField(max_length=50, null=True, blank=True, default=None)
    status = models.CharField(_('status'), max_length=1, choices=INTERFACE_STATUS, default='u')
    added = models.DateTimeField(auto_now_add=True,)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        if self.ipv4_address:
            value = self.ipv4_address
        elif self.ipv6_address:
            value = self.ipv6_address
        elif self.mac_address:
            value = 'MAC: %s' % self.mac_address
        else:
            value = self.device.name
        return value

    class Meta:
        unique_together = (('device', 'cname'),)
        verbose_name = _('Interface')
        verbose_name_plural = _('Interfaces')
        db_table = 'nodeshot_interface'


class OldLink(models.Model):
    from_interface = models.ForeignKey(OldInterface, related_name='from_interface')
    to_interface = models.ForeignKey(OldInterface, related_name='to_interface')
    etx = models.FloatField(default=0)
    dbm = models.IntegerField(default=0)
    sync_tx = models.IntegerField(default=0)
    sync_rx = models.IntegerField(default=0)
    hide = models.BooleanField(_('Hide from map'), default=False)

    def get_quality(self, type='etx'):
        """ used to determine color of links"""
        if type == 'etx':
            if 0 < self.etx < 1.5:
               quality = 1
            elif self.etx < 3:
               quality = 2
            else:
                quality = 3
        elif type == 'dbm':
            if -83 < self.dbm < 0:
                quality = 1
            elif self.dbm > -88:
                quality = 2
            else:
                quality = 3
        return quality

    def get_etx(self):
        """ return etx as a string to avoid dot to comma conversion (it happens only with certain LANGUAGE_CODEs like IT)"""
        return str(self.etx)

    def __unicode__(self):
        return u'%s » %s' % (self.from_interface.device, self.to_interface.device)

    class Meta:
        verbose_name = _('Link')
        verbose_name_plural = _('Links')
        db_table = 'nodeshot_link'


class OldStatistic(models.Model):
    active_nodes = models.IntegerField(_('active nodes'))
    potential_nodes = models.IntegerField(_('potential nodes'))
    hotspots = models.IntegerField(_('hotspots'))
    links = models.IntegerField(_('active links'))
    km = models.FloatField(_('Km'))
    date = models.DateTimeField(_('Added on'), auto_now_add=True)

    def __unicode__(self):
        return u'%s' % (self.date)

    class Meta:
        verbose_name = _('Statistic')
        verbose_name_plural = _('Statistics')
        db_table = 'nodeshot_statistic'


class OldContact(models.Model):
    node = models.ForeignKey(OldNode)
    from_name = models.CharField(_('name'), max_length=50)
    from_email = models.EmailField(_('email'), max_length=50)
    message = models.CharField(_('message'), max_length=2000)
    ip = models.GenericIPAddressField(verbose_name=_('ip address'))
    user_agent = models.CharField(max_length=200, blank=True)
    http_referer = models.CharField(max_length=200, blank=True)
    accept_language = models.CharField(max_length=60, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return _(u'Message from %(from)s to %(to)s') % ({'from':self.from_name, 'to':self.node.name})

    class Meta:
        verbose_name = _('Contact Log')
        verbose_name_plural = _('Contact Logs')
        db_table = 'nodeshot_contact'


# --- users hack --- #

from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.utils import timezone


class OldUser(AbstractBaseUser):
    username = models.CharField(_('username'), max_length=30, unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, numbers and '
                    '@/./+/-/_ characters'))
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    is_superuser = models.BooleanField(_('superuser status'), default=False,
        help_text=_('Designates that this user has all permissions without '
                    'explicitly assigning them.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        app_label = 'oldimporter'
        db_table = 'auth_user'
