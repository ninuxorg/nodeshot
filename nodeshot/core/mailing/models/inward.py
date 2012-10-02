from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.core.mail import EmailMessage
from django.conf import settings
from nodeshot.core.base.models import BaseDate
from choices import INWARD_STATUS


# inward
class Inward(BaseDate):
    # could be a node, an user or a zone
    status = models.IntegerField(_('status'), choices=INWARD_STATUS, default=INWARD_STATUS[1][0])
    limit = models.Q(app_label = 'nodes', model = 'Node') | models.Q(app_label = 'auth', model = 'User') | models.Q(app_label = 'zones', model = 'Zone')
    content_type = models.ForeignKey(ContentType, limit_choices_to = limit)
    object_id = models.PositiveIntegerField()
    to = generic.GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, verbose_name=_('user'), blank=True)
    from_name = models.CharField(_('name'), max_length=50)
    from_email = models.EmailField(_('email'), max_length=50)
    message = models.TextField(_('message'), validators=[
        MaxLengthValidator(settings.NODESHOT['SETTINGS']['CONTACT_INWARD_MAXLENGTH']),
        MinLengthValidator(settings.NODESHOT['SETTINGS']['CONTACT_INWARD_MINLENGTH'])
    ])
    ip = models.GenericIPAddressField(verbose_name=_('ip address'), blank=True, null=True)
    user_agent = models.CharField(max_length=255, blank=True)
    http_referer = models.CharField(max_length=255, blank=True)
    accept_language = models.CharField(max_length=255, blank=True)
    
    class Meta:
        verbose_name = _('Inward message')
        verbose_name_plural = _('Inward messages')
        app_label= 'mailing'
        ordering = ['-status']
    
    def __unicode__(self):
        return _(u'Message from %(from)s to %(to)s') % ({'from':self.from_name, 'to':self.content_type})
    
    def send(self):
        """
        Sends the email to the recipient
        """
        if self.content_type.name == 'node':
            to = self.to.user.email
        else:
            to = self.to.email

        email = EmailMessage(
            # subject
            _('Contact request from %(sender)s - %(site)s') % {'sender': self.from_name, 'site': settings.SITE_NAME},
            # message
            self.message,
            # from
            settings.DEFAULT_FROM_EMAIL,
            # to
            [to],
            # reply-to header
            headers = {'Reply-To': self.from_email}
        )
        email.send()
    
    def save(self, *args, **kwargs):
        """
        Custom save method
        """
        if self.status < 1:
            try:
                self.send()
                self.status = 1
            except Exception, e:
                from logging import error
                error('nodeshot.core.mailing.inward.save(): %s' % e)
                self.status = -1
        
        if settings.NODESHOT['SETTINGS']['CONTACT_INWARD_LOG']:
            super(Inward, self).save(*args, **kwargs)