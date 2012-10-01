from django.db import models
from django.utils.translation import ugettext_lazy as _
from nodeshot.core.base.models import BaseAccessLevel
from nodeshot.core.base.choices import LOGIN_TYPES

class Login(BaseAccessLevel):
    service = models.ForeignKey('services.Service', verbose_name=_('service'))
    type = models.SmallIntegerField(_('type'), max_length=2, choices=LOGIN_TYPES, default=LOGIN_TYPES[0][0])
    username = models.CharField(_('username'), max_length=30) # space should not be allowed
    password = models.CharField(_('password'), max_length=128)
    description = models.CharField(_('description'), max_length=255, blank=True, null=True)
    # unique together username and service
    
    class Meta:
        db_table = 'services_login'
        app_label = 'services'
        permissions = (('can_view_service_login', 'Can view service logins'),)
        verbose_name = _('login')
        verbose_name_plural = _('logins')
    
    def __unicode__(self):
        return '%s - %s' % (self.username, self.service) 