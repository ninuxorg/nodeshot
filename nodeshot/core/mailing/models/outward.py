from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator
from django.conf import settings
from nodeshot.core.base.models import BaseDate
from nodeshot.dependencies.fields import MultiSelectField


SCHEDULE_CHOICES = (
    (0, _("Don't schedule, send immediately")),
    (1, _('Schedule')),
)

RECIPIENT_TYPES = (
    ('all', _('all')),
    ('zones', _('users of the selected zones')),
    ('users', _('chosen users')),
    ('superusers', _('super users'))
)

OUTWARD_STATI = (
    (-1, _('cancelled')),
    (0, _('draft')),
    (1, _('sent')),
    (2, _('scheduled'))
)


class Outward(BaseDate):
    status = models.IntegerField(_('status'), choices=OUTWARD_STATI, default=OUTWARD_STATI[1][0])
    subject = models.CharField(_('subject'), max_length=50)
    message = models.TextField(_('message'), validators=[MaxLengthValidator(settings.NODESHOT['SETTINGS']['CONTACT_OUTWARD_MAXLENGTH'])])
    is_scheduled = models.SmallIntegerField(_('schedule sending'), choices=SCHEDULE_CHOICES, default=1 if settings.NODESHOT['DEFAULTS']['MAILING_SCHEDULE_OUTWARD'] is True else 0)
    scheduled_date = models.DateField(_('scheduled date'), blank=True)
    scheduled_time = models.CharField(_('scheduled time'), max_length=20, choices=settings.NODESHOT['CHOICES']['AVAILABLE_CRONJOBS'], default=settings.NODESHOT['DEFAULTS']['CRONJOB'], blank=True)
    recipient_types = MultiSelectField(max_length=255, blank=True, choices=RECIPIENT_TYPES)
    recipient_groups = MultiSelectField(max_length=255, blank=True, choices=settings.NODESHOT['CHOICES']['ACCESS_LEVELS'])
    
    if 'nodeshot.core.zones' in settings.INSTALLED_APPS:
        zones = models.ManyToManyField('zones.Zone', verbose_name=_('zones'))
    
    users = models.ManyToManyField(User, verbose_name=_('users'))
    
    class Meta:
        verbose_name = _('Outward message')
        verbose_name_plural = _('Outward messages')
        app_label= 'mailing'
    
    def __unicode__(self):
        return '%s' % self.subject