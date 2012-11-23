from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.core.mail import EmailMessage
from django.conf import settings
from nodeshot.core.base.models import BaseDate
from choices import INWARD_STATUS_CHOICES


limit = models.Q(app_label = 'nodes', model = 'Node') | models.Q(app_label = 'auth', model = 'User') | models.Q(app_label = 'zones', model = 'Zone')


class Inward(BaseDate):
    """
    Incoming messages from users
    """
    # could be a node, an user or a zone
    status = models.IntegerField(_('status'), choices=INWARD_STATUS_CHOICES, default=INWARD_STATUS_CHOICES[1][0])
    content_type = models.ForeignKey(ContentType, limit_choices_to=limit)
    object_id = models.PositiveIntegerField()
    to = generic.GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, verbose_name=_('user'), blank=not settings.NODESHOT['SETTINGS']['CONTACT_INWARD_REQUIRE_AUTH'], null=True)
    from_name = models.CharField(_('name'), max_length=50)
    from_email = models.EmailField(_('email'), max_length=50)
    message = models.TextField(_('message'), validators=[
        MaxLengthValidator(settings.NODESHOT['SETTINGS']['CONTACT_INWARD_MAXLENGTH']),
        MinLengthValidator(settings.NODESHOT['SETTINGS']['CONTACT_INWARD_MINLENGTH'])
    ])
    ip = models.GenericIPAddressField(verbose_name=_('ip address'), blank=True, null=True)
    user_agent = models.CharField(max_length=255, blank=True)
    accept_language = models.CharField(max_length=255, blank=True)
    # who fucking cares
    #http_referer = models.CharField(max_length=255, blank=True)
    
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
        If the sending fails will set the status of the instance to "error" and will log the error according to your project's django-logging configuration
        """
        if self.content_type.name == 'node':
            to = [self.to.user.email]
        elif self.content_type.name == 'zone':
            to = [self.to.email]
            # zone case is slightly special, mantainers need to be notified as well
            # TODO: consider making the mantainers able to switch off notifications
            for mantainer in self.to.mantainers.all().only('email'):
                to += [mantainer.email]
        else:
            to = [self.to.email]

        email = EmailMessage(
            # subject
            _('Contact request from %(sender)s - %(site)s') % {'sender': self.from_name, 'site': settings.SITE_NAME},
            # message
            self.message,
            # from
            settings.DEFAULT_FROM_EMAIL,
            # to
            to,
            # reply-to header
            headers = {'Reply-To': self.from_email}
        )
        
        import socket
        # try sending email
        try:
            email.send()            
            self.status = 1
        # if error
        except socket.error as e:
            # log the error
            import logging
            log = logging.getLogger(__name__)
            log.error('nodeshot.core.mailing.models.inward.send(): %s' % e)
            # set status of the instance as "error"
            self.status = -1
    
    def save(self, *args, **kwargs):
        """
        Custom save method
        """
        # if not sent yet
        if int(self.status) < 1:
            # tries sending email (will modify self.status!)
            self.send()
        
        # save in the database unless logging is explicitly turned off in the settings file
        if settings.NODESHOT['SETTINGS']['CONTACT_INWARD_LOG']:
            super(Inward, self).save(*args, **kwargs)