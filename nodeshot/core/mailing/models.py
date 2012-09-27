from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.validators import MaxLengthValidator
from django.conf import settings
from nodeshot.core.base.models import BaseDate
from nodeshot.dependencies.fields import MultiSelectField

# inward
class Inward(BaseDate):
    # could be a node, an user or a zone
    limit = models.Q(app_label = 'nodes', model = 'Node') | models.Q(app_label = 'auth', model = 'User') | models.Q(app_label = 'zones', model = 'Zone')
    content_type = models.ForeignKey(ContentType, limit_choices_to = limit)
    object_id = models.PositiveIntegerField()
    to = generic.GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, verbose_name=_('user'), blank=True)
    from_name = models.CharField(_('name'), max_length=50)
    from_email = models.EmailField(_('email'), max_length=50)
    message = models.TextField(_('message'), validators=[MaxLengthValidator(settings.NODESHOT['SETTINGS']['CONTACT_INWARD_MAXLENGTH'])])
    ip = models.GenericIPAddressField(verbose_name=_('ip address'))
    user_agent = models.CharField(max_length=200, blank=True)
    http_referer = models.CharField(max_length=200, blank=True)
    accept_language = models.CharField(max_length=60, blank=True)
    
    class Meta:
        verbose_name = _('Inward message')
        verbose_name_plural = _('Inward messages')
    
    def __unicode__(self):
        return _(u'Message from %(from)s to %(to)s') % ({'from':self.from_name, 'to':self.node.name})


SCHEDULE_CHOICES = (
    (0, _("Don't schedule, send immediately")),
    (1, _('Schedule')),
)

RECIPIENT_TYPES = (
    ('all', _('all')),
    ('zones', _('zones')),
    ('users', _('chosen users')),
    ('superusers', _('super users'))
)

RECIPIENT_GROUPS = [
    [group for group in settings.NODESHOT['CHOICES']['ACCESS_LEVELS']]
]

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
    recipient_groups = MultiSelectField(max_length=255, blank=True, choices=RECIPIENT_GROUPS)
    
    if 'nodeshot.core.zones' in settings.INSTALLED_APPS:
        zones = models.ManyToManyField('zones.Zone', verbose_name=_('zones'))
    
    users = models.ManyToManyField(User, verbose_name=_('users'))
    
    class Meta:
        verbose_name = _('Outward message')
        verbose_name_plural = _('Outward messages')
    
    def __unicode__(self):
        return '%s' % self.subject