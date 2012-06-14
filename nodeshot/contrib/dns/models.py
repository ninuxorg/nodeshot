# models for nodeshot DNS (integration with powerDNS).

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from nodeshot.core.base.models import BaseDate
from nodeshot.core.nodes.models import Zone, Node
from nodeshot.core.network.models import Device, Interface

ACCESS_LEVELS = (
    ('owner', _('owner')),
    ('manager', _('manager'))
)

#Domain PowerDNS table

class Domain(BaseDate):
    name            = models.CharField(_('name'), max_length=255, unique=True, db_index=True)
    type            = models.CharField(_('type'),max_length=6, choices=((x,x) for x in ('NATIVE', 'MASTER', 'SLAVE', 'SUPERSLAVE')))
    notified_serial = models.PositiveIntegerField(_('notified serial'), null=True, blank=True, default=None)
    master          = models.CharField(_('master'),max_length=128, null=True,blank=True, default=None)
    last_check      = models.PositiveIntegerField(_('last check'), null=True, blank=True, default=None)
    account         = models.CharField(_('account'), max_length=40, null=True, blank=True, default=None)

    class Meta:
        db_table = 'domains'
        ordering = ('name', 'type')

    def __unicode__(self):
        return self.name

#Record PowerDNS table

class Record(BaseDate):
    domain      = models.ForeignKey('Domain', verbose_name=_('domain'))
    name        = models.CharField(_('name'), max_length=255, db_index=True)
    type        = models.CharField(_('type'),max_length=6, db_index=True, choices=((x,x) for x in ('A', 'AAAA', 'AFSDB', 'CERT', 'CNAME', 'DNSKEY', 'DS', 'HINFO', 'KEY', 'LOC', 'MX', 'NAPTR', 'NS', 'NSEC', 'PTR', 'RP', 'RRSIG', 'SOA', 'SPF', 'SSHFP', 'SRV', 'TXT')))
    content     = models.CharField(_('content'),max_length=255)
    ttl         = models.PositiveIntegerField()
    prio        = models.PositiveIntegerField(_('priority'), null=True, blank=True)
    change_date = models.PositiveIntegerField(_('change date'), null=True, blank=True)

    class Meta:
        db_table = 'records'
        ordering = ('name', 'type')
        unique_together = ('name', 'type', 'content')

    def __unicode__(self):
        return self.name

#Supermaster PowerDNS table (deprecated)

class Supermaster(BaseDate):
    nameserver = models.CharField(max_length=255, db_index=True)
    account    = models.CharField(max_length=40, null=True, blank=True, db_index=True)

    class Meta:
        db_table = 'supermasters'
        ordering = ('nameserver', 'account')
        unique_together = ('nameserver', 'account')

    def __unicode__(self):
        return self.nameserver


# Nodeshot

class DomainPolicy(BaseDate):
    domain              = models.ForeignKey(Domain, verbose_name='domain', blank=True, null=True)
    name                = models.CharField(_('name'), max_length=255, unique=True)
    is_automatized      = models.BooleanField(default=False)
    can_request         = models.IntegerField(default=0)
    needs_confirmation  = models.BooleanField(default=False)
    managers            = models.ManyToManyField(User, through='DomainManager', verbose_name=_('name'))


class ZoneToDns(BaseDate):
    zone                = models.OneToOneField(Zone, primary_key=True)
    value               = models.SlugField(_('value'), max_length=20)

class NodeToDns(BaseDate):
    zone                = models.OneToOneField(Node, primary_key=True)
    value               = models.SlugField(_('value'), max_length=20)

class DeviceToDns(BaseDate):
    zone                = models.OneToOneField(Device, primary_key=True)
    value               = models.SlugField(_('value'), max_length=20)

class InterfaceToDns(BaseDate):
    zone                = models.OneToOneField(Interface, primary_key=True)
    value               = models.SlugField(_('value'), max_length=20)


class DomainManager(BaseDate):
    user                = models.ForeignKey(User)
    domain              = models.ForeignKey(DomainPolicy)
    access_level        = models.CharField(_('access level'), max_length=10, choices=ACCESS_LEVELS)
    
    class Meta:
        unique_together = ('user', 'domain')
