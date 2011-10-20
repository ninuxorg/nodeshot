# -*- coding: utf-8 -*-
from django.db import models

import random
from django.utils.hashcompat import sha_constructor
from django.core.mail import send_mail
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify
from nodeshot.utils import notify_admins, email_owners
from django.core.exceptions import ValidationError

# for UserProfile
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# django >= 1.4
try:
    from django.contrib.auth.utils import make_password, check_password
# django <= 1.3
except ImportError:
    from nodeshot.utils import make_password, check_password

from settings import ROUTING_PROTOCOLS, DEFAULT_ROUTING_PROTOCOL, ACTIVATION_DAYS, DEFAULT_FROM_EMAIL, SITE, _

# IS_SCRIPT is defined in management scripts to avoid sending notifications
try:
    IS_SCRIPT
except:
    IS_SCRIPT = False

NODE_STATUS = (
    ('a', _('active')),
    ('p', _('potential')),
    ('h', _('hotspot')),
    ('u', _('unconfirmed')) # nodes that have not been confirmed via email yet
)

INTERFACE_TYPE = (
    ('wifi', _('wifi')),
    ('eth', _('ethernet')),
    ('vpn', _('vpn')),
    ('batman', _('batman')),
    ('bridge', _('bridge')),
    ('vwifi', _('virtual-wifi')),
    ('veth', _('virtual-ethernet'))
)

INTERFACE_STATUS = (
    ('r', _('reachable')),
    ('u', _('unreachable'))
)

WIRELESS_MODE = (
    ('sta', _('sta')),
    ('ap', _('ap')),
    ('adhoc', _('adhoc')),
)

WIRELESS_POLARITY = (
    ('h', _('horizontal')),
    ('v', _('vertical')),
    ('c', _('circular')),
    ('a', _('auto')),
)

WIRELESS_CHANNEL = (
    ('2412', '2.4Ghz Ch  1 (2412 Mhz)'),
    ('2417', '2.4Ghz Ch  2 (2417 Mhz)'),
    ('2422', '2.4Ghz Ch  3 (2422 Mhz)'),
    ('2427', '2.4Ghz Ch  4 (2427 Mhz)'),
    ('2427', '2.4Ghz Ch  5 (2432 Mhz)'),
    ('2437', '2.4Ghz Ch  6 (2437 Mhz)'),
    ('2442', '2.4Ghz Ch  7 (2442 Mhz)'),
    ('2447', '2.4Ghz Ch  8 (2447 Mhz)'),
    ('2452', '2.4Ghz Ch  9 (2452 Mhz)'),
    ('2457', '2.4Ghz Ch  10 (2457 Mhz)'),
    ('2462', '2.4Ghz Ch  11 (2462 Mhz)'),
    ('2467', '2.4Ghz Ch  12 (2467 Mhz)'),
    ('2472', '2.4Ghz Ch  13 (2472 Mhz)'),
    ('2484', '2.4Ghz Ch  14 (2484 Mhz)'),
    ('4915', '5Ghz Ch 183 (4915 Mhz)'),
    ('4920', '5Ghz Ch 184 (4920 Mhz)'),
    ('4925', '5Ghz Ch 185 (4925 Mhz)'),
    ('4935', '5Ghz Ch 187 (4935 Mhz)'),
    ('4940', '5Ghz Ch 188 (4940 Mhz)'),
    ('4945', '5Ghz Ch 189 (4945 Mhz)'),
    ('4960', '5Ghz Ch 192 (4960 Mhz)'),
    ('4980', '5Ghz Ch 196 (4980 Mhz)'),
    ('5035', '5Ghz Ch 7 (5035 Mhz)'),
    ('5040', '5Ghz Ch 8 (5040 Mhz)'),
    ('5045', '5Ghz Ch 9 (5045 Mhz)'),
    ('5055', '5Ghz Ch 11 (5055 Mhz)'),
    ('5060', '5Ghz Ch 12 (5060 Mhz)'),
    ('5080', '5Ghz Ch 16 (5080 Mhz)'),
    ('5170', '5Ghz Ch 34 (5170 Mhz)'),
    ('5180', '5Ghz Ch 36 (5180 Mhz)'),
    ('5190', '5Ghz Ch 38 (5190 Mhz)'),
    ('5200', '5Ghz Ch 40 (5200 Mhz)'),
    ('5210', '5Ghz Ch 42 (5210 Mhz)'),
    ('5220', '5Ghz Ch 44 (5220 Mhz)'),
    ('5230', '5Ghz Ch 46 (5230 Mhz)'),
    ('5240', '5Ghz Ch 48 (5240 Mhz)'),
    ('5260', '5Ghz Ch 52 (5260 Mhz)'),
    ('5280', '5Ghz Ch 56 (5280 Mhz)'),
    ('5300', '5Ghz Ch 60 (5300 Mhz)'),
    ('5320', '5Ghz Ch 64 (5320 Mhz)'),
    ('5500', '5Ghz Ch 100 (5500 Mhz)'),
    ('5520', '5Ghz Ch 104 (5520 Mhz)'),
    ('5540', '5Ghz Ch 108 (5540 Mhz)'),
    ('5560', '5Ghz Ch 112 (5560 Mhz)'),
    ('5580', '5Ghz Ch 116 (5580 Mhz)'),
    ('5600', '5Ghz Ch 120 (5600 Mhz)'),
    ('5620', '5Ghz Ch 124 (5620 Mhz)'),
    ('5640', '5Ghz Ch 128 (5640 Mhz)'),
    ('5660', '5Ghz Ch 132 (5660 Mhz)'),
    ('5680', '5Ghz Ch 136 (5680 Mhz)'),
    ('5700', '5Ghz Ch 140 (5700 Mhz)'),
    ('5745', '5Ghz Ch 149 (5745 Mhz)'),
    ('5765', '5Ghz Ch 153 (5765 Mhz)'),
    ('5785', '5Ghz Ch 157 (5785 Mhz)'),
    ('5805', '5Ghz Ch 161 (5805 Mhz)'),
    ('5825', '5Ghz Ch 165 (5825 Mhz)')
)

class Node(models.Model):
    name = models.CharField(_('name'), max_length=50, unique=True)
    slug = models.SlugField(max_length=50, db_index=True, unique=True)
    owner = models.CharField(_('owner'), max_length=50, blank=True, null=True)
    description = models.CharField(_('description'), max_length=200, blank=True, null=True)
    postal_code = models.CharField(_('postal code'), max_length=10)
    email = models.EmailField()
    email2 = models.EmailField(blank=True, null=True)
    email3 = models.EmailField(blank=True, null=True)
    password =  models.CharField(max_length=255, help_text=_('Use "[algo]$[salt]$[hexdigest]" or use the  <a href="password/">change password form</a>.'))
    lat = models.FloatField(_('latitude'))
    lng = models.FloatField(_('longitude')) 
    alt = models.FloatField(_('altitude'), blank=True, null=True)
    status = models.CharField(_('status'), max_length=1, choices=NODE_STATUS, default='p')
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
    
    def set_password(self):
        """
        Encrypts node.password with salt and sha1.
        The password property must have been set previously (node.password = 'rawpassword')
        """
        self.password = make_password('sha1', self.password)
        return self.password
    
    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        encryption formats behind the scenes.
        """
        return check_password(raw_password, self.password)
        
    def reset_password(self, petitioner):
        """
        Resets the password of a node and send an email to the owners with the new password.
        petitioner: string containing the email address of who's requesting the password reset
        returns the raw password
        """
        import random
        bit1 = ''.join(random.choice('abcdefghilmnopqrstuvz') for i in xrange(5))
        bit2 = ''.join(random.choice('0123456789') for i in xrange(2))
        raw_password = bit1 + bit2
        self.password = raw_password
        self.set_password()
        self.save()
        # prepare context
        context = {
            'petitioner': petitioner,
            'node': self,
            'password': raw_password,
            'site': SITE
        }
        # send mail
        email_owners(self, _('New password for node %(name)s') % {'name':self.name}, 'email_notifications/password_recovery.txt', context)
        return raw_password
    
    def set_activation_key(self):
        ''' Set the activation key, generate it from a combinatin of the ''Node''s name and a random salt '''
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        self.activation_key = sha_constructor(salt+self.name).hexdigest()
        return self.activation_key
    
    def send_activation_mail(self):
        """
        Sends activation link to node owners
        """
        # prepare context for email template
        context = {
            'node': self,
            'expiration_days': ACTIVATION_DAYS,
            'site': SITE,
        }
        # send mail to owners
        email_owners(self, _('Node confirmation required on %(site)s') % {'site':SITE['name']}, 'email_notifications/confirmation.txt', context)
        
    def send_success_mail(self, raw_password):
        ''' send success emails '''
        # prepare context
        context = {
            'node': self,
            'password': raw_password,
            'site': SITE
        }
        # send email to owners
        email_owners(self, _('Node confirmed successfully on %(site)s') % {'site':SITE['name']}, 'email_notifications/success.txt', context)
        # notify admins that want to receive notifications
        notify_admins(self, _('New node details on %(site)s') % {'site':SITE['name']}, 'email_notifications/new-node-admin.txt', context, skip=True)
        
    def confirm(self):
        '''
            * change status from ''unconfirmed'' to ''potential''
            * clear the ''activation_key'' field
            * encrypt password
            * send email with details of the node to owners
        '''
        self.status = 'p'
        self.activation_key = ''
        raw_password = self.password
        self.set_password()
        self.save()
        self.send_success_mail(raw_password)
        
    def save(self):
        ''' Override the save method in order to generate the activation key for new nodes. '''
        # generate slug if needed
        if self.slug == '':
            self.slug = slugify(self.name)
        # if saving a new object
        if self.pk is None and not IS_SCRIPT:
            self.set_activation_key()
            super(Node, self).save()
            # confirmation email is sent afterwards so we can send the ID
            self.send_activation_mail()
        else:
            super(Node, self).save()
    
    def __unicode__(self):
        return u'%s' % (self.name)
    
    class Meta:
        verbose_name = _('Node')
        verbose_name_plural = _('Nodes')

class Device(models.Model):
    name = models.CharField(_('name'), max_length=50, unique=True)
    description = models.CharField(_('description'), max_length=255, blank=True, null=True)
    type = models.CharField(_('type'), max_length=50, blank=True, null=True) 
    node = models.ForeignKey(Node, verbose_name=_('node'))
    routing_protocol = models.CharField(_('routing protocol'), max_length=20, choices=ROUTING_PROTOCOLS, default=DEFAULT_ROUTING_PROTOCOL)
    routing_protocol_version = models.CharField(_('routing protocol version'), max_length=10, blank=True, null=True)
    added = models.DateTimeField(_('added on'), auto_now_add=True)
    updated = models.DateTimeField(_('updated on'), auto_now=True)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = _('Device')
        verbose_name_plural = _('Devices')

class Hna(models.Model):
    device = models.ForeignKey(Device)
    route = models.CharField(max_length=20)
    
    def __unicode__(self):
        return u'%s' % (self.route)
        
    class Meta:
        verbose_name = _('Hna')
        verbose_name_plural = _('Hna')

class Interface(models.Model):
    ipv4_address = models.IPAddressField(verbose_name=_('ipv4 address'), blank=True, null=True, unique=True, default=None)
    ipv6_address = models.GenericIPAddressField(protocol='IPv6', verbose_name=_('ipv6 address'), blank=True, null=True, unique=True, default=None)
    mac_address = models.CharField(max_length=17, blank=True, null=True, unique=True, default=None)
    type = models.CharField(max_length=10, choices=INTERFACE_TYPE)
    device = models.ForeignKey(Device)
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
    
    def clean(self):
        """
        Require at least one of ipv4 or ipv6 to be set
        """
        if not (self.ipv4_address or self.ipv6_address or self.mac_address):
            raise ValidationError(_('At least one of the following field is necessary: IPv4, IPv6 or Mac address.'))
    
    class Meta:
        verbose_name = _('Interface')
        verbose_name_plural = _('Interfaces')

class Link(models.Model):
    from_interface = models.ForeignKey(Interface, related_name='from_interface')
    to_interface = models.ForeignKey(Interface, related_name='to_interface')
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
    
class Statistic(models.Model):
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

class Contact(models.Model):
    node = models.ForeignKey(Node)
    from_name = models.CharField(_('name'), max_length=50)
    from_email = models.EmailField(_('email'), max_length=50)
    message = models.CharField(_('message'), max_length=2000)
    ip = models.GenericIPAddressField(verbose_name=_('ip address'))
    user_agent = models.CharField(max_length=200, blank=True)
    http_referer = models.CharField(max_length=200, blank=True)
    accept_language = models.CharField(max_length=30, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return _(u'Message from %(from)s to %(to)s') % ({'from':self.from_name, 'to':self.node.name})
    
    class Meta:
        verbose_name = _('Contact Log')
        verbose_name_plural = _('Contact Logs')
    
class UserProfile(models.Model):
    """
    Extending django's user model so we can have an additional field
    where we can specify if admins should receive notifications or not
    
    https://docs.djangoproject.com/en/dev/topics/auth/#storing-additional-information-about-users
    """
    
    user = models.OneToOneField(User)
    receive_notifications = models.BooleanField(_('Email notifications'), help_text=_('Activate/deactivate email notifications about the management of the map server (added nodes, deleted nodes, abuses, ecc).'))
    
# init nodeshot signals
import signals
