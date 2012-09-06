# models for nodeshot DNS (integration with powerDNS).

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from nodeshot.core.base.models import BaseDate
from nodeshot.core.network.models import Device, Interface

import hashlib

ACCESS_LEVELS = (
    ('owner', _('owner')),
    ('manager', _('manager'))
)

DOMAIN_TYPE = (
    'NATIVE',
    'MASTER',
    'SLAVE',
    'SUPERSLAVE'
)

RECORD_TYPE = ( #Can be implemented into a table with USER_RECORD_TYPE  
    'A',
    'AAAA',
    'AFSDB',
    'CERT',
    'CNAME',
    'DNSKEY',
    'DS',
    'HINFO',
    'KEY',
    'LOC',
    'MX',
    'NAPTR',
    'NS',
    'NSEC',
    'PTR',
    'RP',
    'RRSIG',
    'SOA',
    'SPF',
    'SSHFP',
    'SRV',
    'TXT'
)

USER_RECORD_TYPE = (
    'A',
    'AAAA',
    'CNAME',
    'MX'
)

class Domain(BaseDate):
    """
    Domain PowerDNS table
    """
    name            = models.CharField(_('name'), max_length=255, unique=True, db_index=True)
    type            = models.CharField(_('type'),max_length=6, choices=((x,x) for x in DOMAIN_TYPE))
    notified_serial = models.PositiveIntegerField(_('notified serial'), null=True, blank=True, default=None)
    master          = models.CharField(_('master'),max_length=128, null=True,blank=True, default=None)
    last_check      = models.PositiveIntegerField(_('last check'), null=True, blank=True, default=None)
    account         = models.CharField(_('account'), max_length=40, null=True, blank=True, default=None)

    class Meta:
        db_table = 'domains'
        ordering = ('name', 'type')

    def __unicode__(self):
        return self.name


class Record(BaseDate):
    """
    Record PowerDNS table
    """
    domain      = models.ForeignKey('Domain', verbose_name=_('domain'))
    name        = models.CharField(_('name'), max_length=255, db_index=True)
    type        = models.CharField(_('type'),max_length=6, db_index=True, choices=((x,x) for x in RECORD_TYPE))
    content     = models.CharField(_('content'),max_length=255)
    ttl         = models.PositiveIntegerField()
    prio        = models.PositiveIntegerField(_('priority'), null=True, blank=True)
    change_date = models.PositiveIntegerField(_('change date'), null=True, blank=True)
    is_automatized = models.BooleanField(_('is automatized'), default=False)
    md5hash     = models.CharField(_('hash'), max_length=32, null=True, blank=True)

    class Meta:
        db_table = 'records'
        ordering = ('name', 'type')
        unique_together = ('name', 'type', 'content')

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        id_hash = hashlib.md5(self.name + self.type + self.content).hexdigest()
        self.md5hash = id_hash
        super(Record, self).save(*args, **kwargs)




class Supermaster(BaseDate):
    """
    Supermaster PowerDNS table (deprecated)
    """
    nameserver = models.CharField(max_length=255, db_index=True)
    account    = models.CharField(max_length=40, null=True, blank=True, db_index=True)

    class Meta:
        db_table = 'supermasters'
        ordering = ('nameserver', 'account')
        unique_together = ('nameserver', 'account')

    def __unicode__(self):
        return self.nameserver

"""
OneToOne tables for customize automatic DNS names
"""
class ZoneToDns(models.Model):
    zone                = models.OneToOneField('zones.Zone', db_index=True, unique=True)
    value               = models.SlugField(_('value'), max_length=20)

class NodeToDns(models.Model):
    zone                = models.OneToOneField('nodes.Node', db_index=True, unique=True)
    value               = models.SlugField(_('value'), max_length=20)

class DeviceToDns(models.Model):
    zone                = models.OneToOneField(Device, db_index=True, unique=True)
    value               = models.SlugField(_('value'), max_length=20)

class InterfaceToDns(models.Model):
    zone                = models.OneToOneField(Interface, db_index=True)
    value               = models.SlugField(_('value'), max_length=20)



class DomainPolicy(BaseDate):
    """
    Domains and Subdomains restrictions and policies for users
    """
    name                = models.CharField(max_length=255, db_index=True, unique=True)
    domain              = models.ForeignKey(Domain)
    is_automatized      = models.BooleanField(default=False)
    can_request         = models.IntegerField(default=0)
    needs_confirmation  = models.BooleanField(default=False)
    managers            = models.ManyToManyField(User, through='DomainManager', verbose_name=_('name'))

    def __unicode__(self):
        return u'%s' % self.domain.name

class DomainManager(BaseDate):
    """
    ManyToMany relation between users and (sub)domains
    """
    user                = models.ForeignKey(User)
    domain              = models.ForeignKey(DomainPolicy)
    access_level        = models.CharField(_('access level'), max_length=10, choices=ACCESS_LEVELS)
    
    class Meta:
        unique_together = ('user', 'domain')

class UserRecord(Record):
    """
    User's Records table
    """

    user                 = models.ForeignKey(User)

class DNSScriptCache(models.Model):
    """
    DNS Script Caching table
        name is the domain without the extension
        content is the IPv4/IPv6 Address
    """
    name                = models.CharField(_('name'), max_length=255)
    content             = models.CharField(max_length=29)

