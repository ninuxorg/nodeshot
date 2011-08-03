# -*- coding: utf-8 -*-
from django.db import models

import random
from django.utils.hashcompat import sha_constructor
from django.core.mail import send_mail
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string
from nodeshot.utils import notify_admins

# for UserProfile
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# django >= 1.4
try:
    from django.contrib.auth.utils import make_password
# django <= 1.3
except ImportError:
    from nodeshot.utils import make_password

try:
    from settings import NODESHOT_ROUTING_PROTOCOLS as ROUTING_PROTOCOLS, NODESHOT_DEFAULT_ROUTING_PROTOCOL as DEFAULT_ROUTING_PROTOCOL
except ImportError:
    ROUTING_PROTOCOLS = (
        ('aodv','AODV'),
        ('batman','B.A.T.M.A.N.'),
        ('dsdv','DSDV'),
        ('dsr','DSR'),
        ('hsls','HSLS'),
        ('iwmp','IWMP'),
        ('olsr','OLSR'),
        ('oorp','OORP'),
        ('ospf','OSPF'),
        ('tora','TORA'),
    )
    DEFAULT_ROUTING_PROTOCOL = 'olsr'

try:
    from settings import NODESHOT_ACTIVATION_DAYS as ACTIVATION_DAYS
except ImportError:
    ACTIVATION_DAYS = 7
    
try:
    from settings import DEFAULT_FROM_EMAIL
except ImportError:
    raise ImproperlyConfigured('DEFAULT_FROM_EMAIL is not defined in your settings.py. See settings.example.py for reference.')
    
try:
    from settings import NODESHOT_SITE as SITE
except ImportError:
    raise ImproperlyConfigured('NODESHOT_SITE is not defined in your settings.py. See settings.example.py for reference.')

# IMPORTING is a variable that must be inserted dinamically in scripts that might import this file in order to perform automatic imports from other map servers (for example WNMAP)
try:
    from settings import IMPORTING
except ImportError:
    IMPORTING = False

NODE_STATUS = (
    ('a', 'active'),
    ('p', 'potential'),
    ('h', 'hotspot'),
    ('u', 'unconfirmed') # nodes that have not been confirmed via email yet
)

INTERFACE_TYPE = (
    ('w', 'wifi'),
    ('e', 'ethernet'),
    ('v', 'vpn')
)

INTERFACE_STATUS = (
    ('r', 'reachable'),
    ('u', 'unreachable')
)

WIRELESS_MODE = (
    ('sta', 'sta'),    
    ('ap', 'ap'),    
    ('adhoc', 'adhoc'),    
)

WIRELESS_POLARITY = (
        ('h', 'horizontal'),
        ('v', 'vertical'),
        ('c', 'circular'),
        ('a', 'auto'),
)

WIRELESS_CHANNEL = (
    ('2412', '2.4Ghz Ch  1 (2412 Mhz'), 
    ('2417', '2.4Ghz Ch  2 (2417 Mhz'), 
    ('2422', '2.4Ghz Ch  3 (2422 Mhz'), 
    ('2427', '2.4Ghz Ch  4 (2427 Mhz'), 
    ('2427', '2.4Ghz Ch  5 (2432 Mhz'), 
    ('2437', '2.4Ghz Ch  6 (2437 Mhz'), 
    ('2442', '2.4Ghz Ch  7 (2442 Mhz'), 
    ('2447', '2.4Ghz Ch  8 (2447 Mhz'), 
    ('2452', '2.4Ghz Ch  9 (2452 Mhz'), 
    ('2457', '2.4Ghz Ch  10 (2457 Mhz'), 
    ('2462', '2.4Ghz Ch  11 (2462 Mhz'), 
    ('2467', '2.4Ghz Ch  12 (2467 Mhz'), 
    ('2472', '2.4Ghz Ch  13 (2472 Mhz'), 
    ('2484', '2.4Ghz Ch  14 (2484 Mhz'), 
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
    name = models.CharField('nome', max_length=50, unique=True)
    slug = models.SlugField(max_length=50, db_index=True, unique=True)
    owner = models.CharField('proprietario', max_length=50, blank=True, null=True)
    description = models.CharField('descrizione', max_length=200, blank=True, null=True)
    postal_code = models.CharField('CAP', max_length=10)
    email = models.EmailField()
    email2 = models.EmailField(blank=True, null=True)
    email3 = models.EmailField(blank=True, null=True)
    password =  models.CharField(max_length=255, help_text='Per cambiare la password usa il <a href=\"password/\">form di cambio password</a>.')
    lat = models.FloatField('latitudine')
    lng = models.FloatField('longitudine') 
    alt = models.FloatField('altitudine', blank=True, null=True)
    status = models.CharField('stato', max_length=1, choices=NODE_STATUS, default='p')
    activation_key = models.CharField('chiave di attivazione', max_length=40, blank=True, null=True, help_text='Chiave per la conferma via mail del nodo. Viene cancellata una volta che il nodo è stato attivato.')
    notes = models.TextField('note', blank=True, null=True)
    added = models.DateTimeField('aggiunto il', auto_now_add=True)
    updated = models.DateTimeField('aggiornato il', auto_now=True)
    
    def set_password(self):
        ''' Set the password like django does '''
        self.password = make_password('sha1', self.password)
        return self.password
    
    def set_activation_key(self):
        ''' Set the activation key, generate it from a combinatin of the ''Node''s name and a random salt '''
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        self.activation_key = sha_constructor(salt+self.name).hexdigest()
        return self.activation_key
    
    def send_confirmation_mail(self):
        ''' send activation link to main email and notify the other 2 emails if specified '''
        # prepare context for email template
        context = {
            'node': self,
            'expiration_days': ACTIVATION_DAYS,
            'site': SITE,
        }
        # parse subjects
        subject = render_to_string('email_notifications/confirmation_subject.txt',context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        # parse message
        message = render_to_string('email_notifications/confirmation_body.txt',context)
        # send email to main email
        send_mail(subject, message, DEFAULT_FROM_EMAIL, [self.email])
        
        # if specified, send notifications to the other two email addresses 
        if(self.email2 != '' and self.email2 != None) or (self.email3 != '' and self.email3 != None):
            # prepare context for email template
            context = {
                'node': self,
                'site': SITE
            }
            # parse subject (same for both)
            subject = render_to_string('email_notifications/notify-added-emals_subject.txt',context)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())            
            # initialize an empty list
            recipient_list = []
            # add email2 to the list
            if self.email2 != '' and self.email2 != None:
                recipient_list += [self.email2]
            # add email3 to the list
            if self.email3 != '' and self.email3 != None:
                recipient_list += [self.email3]
            # loop over recipient_list
            for recipient in recipient_list:
                # insert current email in the body text
                context['email'] = recipient
                message = render_to_string('email_notifications/notify-added-emals_body.txt',context)
                # send mail
                send_mail(subject, message, DEFAULT_FROM_EMAIL, (recipient,))
        
    def send_success_mail(self, raw_password):
        ''' send success emails '''
        # prepare context
        context = {
            'node': self,
            'password': raw_password,
            'site': SITE
        }
        # parse subject
        subject = render_to_string('email_notifications/success_subject.txt',context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        # parse message
        message = render_to_string('email_notifications/success_body.txt',context)
        # send email to all the owners        
        recipient_list = [self.email]
        if self.email2 != '' and self.email2 != None:
            recipient_list += [self.email2]
        if self.email3 != '' and self.email3 != None:
            recipient_list += [self.email3]
        # send mail
        send_mail(subject, message, DEFAULT_FROM_EMAIL, recipient_list)
        # notify admins that want to receive notifications
        notify_admins(self, 'email_notifications/new-node-admin_subject.txt', 'email_notifications/new-node-admin_body.txt', context, skip=True)
        
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
        # if saving a new object
        if self.pk is None and not IMPORTING:
            self.set_activation_key()
            super(Node, self).save()
            # confirmation email is sent afterwards so we can send the ID
            self.send_confirmation_mail()
        else:
            super(Node, self).save()
    
    def __unicode__(self):
        return u'%s' % (self.name)
    
    class Meta:
        verbose_name = 'nodo'
        verbose_name_plural = 'nodi'

class Device(models.Model):
    name = models.CharField('nome', max_length=50)
    description = models.CharField('descrizione', max_length=255, blank=True, null=True)
    type = models.CharField('tipo', max_length=50, blank=True, null=True) 
    node = models.ForeignKey(Node, verbose_name='nodo')
    routing_protocol = models.CharField('protocollo di routing', max_length=20, choices=ROUTING_PROTOCOLS, default=DEFAULT_ROUTING_PROTOCOL)
    routing_protocol_version = models.CharField('versione protocollo di routing', max_length=10, blank=True, null=True)
    added = models.DateTimeField('aggiunto il', auto_now_add=True)
    updated = models.DateTimeField('aggiornato il', auto_now=True)
    
    def __unicode__(self):
        return u'%s (%s)' % (self.type, self.node.name )

class HNAv4(models.Model):
    device = models.ForeignKey(Device)
    route = models.CharField(max_length=20)
    
    def __unicode__(self):
        return u'%s' % (self.route)

class Interface(models.Model):
    ipv4_address = models.CharField(max_length=15, unique=True)
    ipv6_address = models.CharField(max_length=50, blank=True, null=True)
    type = models.CharField(max_length=1, choices=INTERFACE_TYPE)
    device = models.ForeignKey(Device)
    wireless_mode = models.CharField(max_length=5, choices=WIRELESS_MODE, blank=True, null=True)
    wireless_channel = models.CharField(max_length=4, choices=WIRELESS_CHANNEL, blank=True, null=True)
    wireless_polarity = models.CharField(max_length=1, choices=WIRELESS_POLARITY, blank=True, null=True)
    mac_address = models.CharField(max_length=17, blank=True, null=True)
    ssid = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField('stato', max_length=1, choices=INTERFACE_STATUS, default='r')
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return u'IP: %s' % (self.ipv4_address)

class Link(models.Model):
    from_interface = models.ForeignKey(Interface, related_name='from_interface')
    to_interface = models.ForeignKey(Interface, related_name='to_interface')
    etx = models.FloatField(default=0)
    dbm = models.IntegerField(default=0)
    sync_tx = models.IntegerField(default=0)
    sync_rx = models.IntegerField(default=0)
    
class Statistic(models.Model):
    active_nodes = models.IntegerField('nodi attivi')
    potential_nodes = models.IntegerField('nodi potenziali')
    hotspots = models.IntegerField('hotspots')
    links = models.IntegerField('Link attivi')
    km = models.FloatField('Km')
    date = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return u'%s' % (self.date)
    
    class Meta:
        verbose_name = 'Statistica'
        verbose_name_plural = 'Statistiche'

class Contact(models.Model):
    node = models.ForeignKey(Node)
    from_name = models.CharField('nome', max_length=50)
    from_email = models.EmailField('email', max_length=50)
    message = models.CharField('messaggio', max_length=2000)
    ip = models.GenericIPAddressField(verbose_name='indirizzo ip')
    user_agent = models.CharField(max_length=200, blank=True)
    http_referer = models.CharField(max_length=200, blank=True)
    accept_language = models.CharField(max_length=30, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return u'Message from %s to %s' % (self.from_name, self.node.name)
    
    class Meta:
        verbose_name = 'Log contatto'
        verbose_name_plural = 'Log Contatti'
    
class UserProfile(models.Model):
    '''
    Extending django's user model so we can have an additional field
    where we can specify if admins should receive notifications or not
    
    https://docs.djangoproject.com/en/dev/topics/auth/#storing-additional-information-about-users
    '''
    user = models.OneToOneField(User)
    receive_notifications = models.BooleanField('Notifiche via email', help_text='Attiva/disattiva le notifiche email riguardanti la gestione dei nodi (aggiunta, cancellazione, abusi, ecc).')

# signals
from django.db.models.signals import post_delete, post_save
from settings import DEBUG
from datetime import datetime, timedelta

def notify_on_delete(sender, instance, using, **kwargs):
    ''' Notify admins when nodes are deleted. Only for production use '''
    # if in testing modedon't send emails
    if DEBUG:
        return False
    # if purging old unconfirmed nodes don't send emails
    if instance.status == 'u' and instance.added + timedelta(days=ACTIVATION_DAYS) < datetime.now():
        return False
    # prepare context
    context = {
        'node': instance,
        'site': SITE
    }
    # notify admins that want to receive notifications
    notify_admins(instance, 'email_notifications/node-deleted-admin_subject.txt', 'email_notifications/node-deleted-admin_body.txt', context, skip=False)

post_delete.connect(notify_on_delete, sender=Node)

from utils import distance
from django.db.models import Q, Count

def update_statistics(sender, instance, using, **kwargs):
    ''' Adds a new record in the statistic table if needed. Called by signals '''
    # retrieve links, select_related() reduces the number of queries, only() selects only the fields we need
    links = Link.objects.all().select_related().only(
        'from_interface__device__node__lat', 'from_interface__device__node__lng',
        'to_interface__device__node__lat', 'to_interface__device__node__lng'
    )
    
    # get counts of the active nodes, potential nodes, hotspots and group the results
    # Count() is a function provided by django.db.models
    nodes = Node.objects.values('status').annotate(count=Count('status')).filter(Q(status='a') | Q(status='h') | Q(status='p')).order_by('status')
    # evaluate queryset to avoid repeating the same query
    nodes = list(nodes)
    
    # active nodes
    active_nodes = nodes[0].get('count')
    # hotspots
    hotspots = nodes[1].get('count')
    # potential nodes
    potential_nodes = nodes[2].get('count')
    # number of links
    link_count = Link.objects.count()
    
    # calculate total km of the links
    km = 0
    for l in links:
        km += distance((l.from_interface.device.node.lat,l.from_interface.device.node.lng), (l.to_interface.device.node.lat, l.to_interface.device.node.lng))
    km = '%0.3f' % km
    
    # retrieve last statistic
    try:
        last = Statistic.objects.all().order_by('-pk')[:1][0]
    # no statistics in the database yet
    except IndexError:
        last = False
    
    # compare last statistic with data we have now (km are converted to string in order to avoid django to mess the comparation caused by float field)
    if last and last.active_nodes == active_nodes and last.hotspots == hotspots and last.potential_nodes == potential_nodes and last.links == link_count and str(last.km) == str(km):
        # if data is the same there's no need to add a new record
        return False
    else:
        # if we got different numbers it means something has changed and we need to insert a new record in the statistics
        new = Statistic(active_nodes=active_nodes, potential_nodes=potential_nodes, hotspots=hotspots, links=link_count, km=km)
        new.save()

# signals to update statistics every time something is modified or deleted
post_delete.connect(update_statistics, sender=Node)
post_delete.connect(update_statistics, sender=Device)
post_delete.connect(update_statistics, sender=Interface)
post_delete.connect(update_statistics, sender=Link)
post_delete.connect(update_statistics, sender=HNAv4)

post_save.connect(update_statistics, sender=Node)
post_save.connect(update_statistics, sender=Device)
post_save.connect(update_statistics, sender=Interface)
post_save.connect(update_statistics, sender=Link)
post_save.connect(update_statistics, sender=HNAv4)

