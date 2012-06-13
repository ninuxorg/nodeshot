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

class Service(BaseAccessLevel):
    device = models.ForeignKey(Device, verbose_name=_('device'))
    ips = models.ManyToManyField(Ip, verbose_name=_('ip addresses'))
    name = models.CharField(_('name'), max_length=30)
    category = models.ForeignKey(ServiceCategory, verbose_name=_('category') )
    description = models.TextField(_('description'), blank=True, null=True)
    uri = models.CharField(_('URI'), max_length=255, blank=True, null=True)
    documentation_url = models.URLField(_('documentation url'), blank=True, null=True)
    status = models.SmallIntegerField(_('status'), choices=SERVICE_STATUS)
    is_active = models.BooleanField(_('active'), default=True)

class ServicePort(BaseDate):
    service = models.ForeignKey(Service, verbose_name=_('service'))
    port = models.IntegerField(_('port'))
    protocol = models.CharField(_('protocol'), max_length=5, choices=PORT_PROTOCOLS, default=PORT_PROTOCOLS[1][0])
    
    class Meta:
        db_table = 'services_service_port'

class ServiceLogin(BaseDate):
    access_level = models.CharField(_('type'), max_length=10, choices=ACCESS_LEVELS, default=ACCESS_LEVELS[1][0])
    service = models.ForeignKey(Service, verbose_name=_('service'))
    type = models.CharField(_('type'), max_length=10, choices=LOGIN_TYPES, default=LOGIN_TYPES[0][0])
    username = models.CharField(_('username'), max_length=30) # space should not be allowed
    password = models.CharField(_('password'), max_length=128)
    description = models.CharField(_('description'), max_length=255, blank=True, null=True)
    # unique together username and service
    
    class Meta:
        db_table = 'services_login'
