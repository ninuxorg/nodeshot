from django.db import models
from django.utils.translation import ugettext_lazy as _
from nodeshot.core.base.models import BaseDate, BaseAccessLevel
from nodeshot.core.network.models import Device, Ip
from nodeshot.core.base.choices import PORT_PROTOCOLS, SERVICE_STATUS, ACCESS_LEVELS, LOGIN_TYPES

class ServiceCategory(BaseDate):
    name = models.CharField(_('name'), max_length=30)
    description = models.TextField(_('description'), blank=True, null=True)
    
    class Meta:
        db_table = 'services_category'
        verbose_name = _('category')
        verbose_name_plural = _('categories')
    
    def __unicode__(self):
        return '%s' % self.name

class Service(BaseAccessLevel):
    device = models.ForeignKey(Device, verbose_name=_('device'))
    ips = models.ManyToManyField(Ip, verbose_name=_('ip addresses'))
    name = models.CharField(_('name'), max_length=30)
    category = models.ForeignKey(ServiceCategory, verbose_name=_('category') )
    description = models.TextField(_('description'), blank=True, null=True)
    uri = models.CharField(_('URI'), max_length=255, blank=True, null=True)
    documentation_url = models.URLField(_('documentation url'), blank=True, null=True)
    status = models.SmallIntegerField(_('status'), choices=SERVICE_STATUS)
    is_published = models.BooleanField(_('published'), default=True)
    
    class Meta:
        permissions = (('can_view_services', 'Can view services'),)
        verbose_name = _('service')
        verbose_name_plural = _('services')
    
    def __unicode__(self):
        return '%s (%s)' % (self.name, self.device.name)

class ServicePort(BaseDate):
    service = models.ForeignKey(Service, verbose_name=_('service'))
    port = models.IntegerField(_('port'))
    protocol = models.CharField(_('protocol'), max_length=5, choices=PORT_PROTOCOLS, default=PORT_PROTOCOLS[1][0])
    description = models.CharField(_('description'), max_length=255, blank=True)
    
    class Meta:
        db_table = 'services_service_port'
        verbose_name = _('port')
        verbose_name_plural = _('ports')
    
    def __unicode__(self):
        return '%s' % self.port 

class ServiceLogin(BaseAccessLevel):
    service = models.ForeignKey(Service, verbose_name=_('service'))
    type = models.SmallIntegerField(_('type'), max_length=2, choices=LOGIN_TYPES, default=LOGIN_TYPES[0][0])
    username = models.CharField(_('username'), max_length=30) # space should not be allowed
    password = models.CharField(_('password'), max_length=128)
    description = models.CharField(_('description'), max_length=255, blank=True, null=True)
    # unique together username and service
    
    class Meta:
        db_table = 'services_login'
        permissions = (('can_view_service_login', 'Can view service logins'),)
        verbose_name = _('login')
        verbose_name_plural = _('logins')
    
    def __unicode__(self):
        return '%s - %s' % (self.username, self.service) 
