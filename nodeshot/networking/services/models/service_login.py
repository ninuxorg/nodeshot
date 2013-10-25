from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.base.models import BaseAccessLevel
from nodeshot.core.base.managers import AccessLevelManager

from .choices import LOGIN_TYPES


class ServiceLogin(BaseAccessLevel):
    service = models.ForeignKey('services.Service',
                                verbose_name=_('service'))
    type = models.SmallIntegerField(_('type'), max_length=2,
                                    choices=LOGIN_TYPES,
                                    default=LOGIN_TYPES[0][0])
    username = models.CharField(_('username'), max_length=30)  # space should not be allowed
    password = models.CharField(_('password'), max_length=128)
    description = models.CharField(_('description'), max_length=255, blank=True, null=True)
    
    objects = AccessLevelManager()
    
    class Meta:
        app_label= 'services'
        db_table = 'service_logins'
        permissions = (('can_view_service_login', 'Can view service logins'),)
        verbose_name = _('login')
        verbose_name_plural = _('logins')
        unique_together = ('username', 'service')
    
    def __unicode__(self):
        return '%s - %s' % (self.username, self.service) 