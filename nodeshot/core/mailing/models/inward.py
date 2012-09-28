from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.validators import MaxLengthValidator
from django.conf import settings
from nodeshot.core.base.models import BaseDate

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
        app_label= 'mailing'
    
    def __unicode__(self):
        return _(u'Message from %(from)s to %(to)s') % ({'from':self.from_name, 'to':self.node.name})