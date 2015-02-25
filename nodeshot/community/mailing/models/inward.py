from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from nodeshot.core.base.models import BaseDate

from .choices import INWARD_STATUS_CHOICES
from ..settings import settings, INWARD_REQUIRE_AUTH, INWARD_MAXLENGTH, INWARD_MINLENGTH, INWARD_LOG


user_app_label = settings.AUTH_USER_MODEL.split('.')[0]
user_model_name = settings.AUTH_USER_MODEL.split('.')[1]
limit = (
    models.Q(app_label='nodes', model='node') |
    models.Q(app_label=user_app_label, model=user_model_name.lower()) |
    models.Q(app_label='layers', model='layer')
)
USER_CAN_BE_BLANK = not INWARD_REQUIRE_AUTH


class Inward(BaseDate):
    """
    Incoming messages from users
    """
    # could be a node, an user or a layer
    status = models.IntegerField(_('status'), choices=INWARD_STATUS_CHOICES, default=INWARD_STATUS_CHOICES[1][0])
    content_type = models.ForeignKey(ContentType, limit_choices_to=limit)
    object_id = models.PositiveIntegerField()
    to = generic.GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'), blank=USER_CAN_BE_BLANK, null=True)
    from_name = models.CharField(_('name'), max_length=50, blank=True)
    from_email = models.EmailField(_('email'), max_length=50, blank=True)
    message = models.TextField(_('message'), validators=[
        MaxLengthValidator(INWARD_MAXLENGTH),
        MinLengthValidator(INWARD_MINLENGTH)
    ])
    ip = models.GenericIPAddressField(verbose_name=_('ip address'), blank=True, null=True)
    user_agent = models.CharField(max_length=255, blank=True)
    accept_language = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = _('Inward message')
        verbose_name_plural = _('Inward messages')
        app_label = 'mailing'
        ordering = ['-status']

    def __unicode__(self):
        return _(u'Message from %(from)s to %(to)s') % ({'from': self.from_name, 'to': self.content_type})

    def clean(self, *args, **kwargs):
        """ custom validation """
        if not self.user and (not self.from_name or not self.from_email):
            raise ValidationError(_('If sender is not specified from_name and from_email must be filled in.'))
        # fill name and email
        if self.user:
            self.from_name = self.user.get_full_name()
            self.from_email = self.user.email

    def send(self):
        """
        Sends the email to the recipient
        If the sending fails will set the status of the instance to "error" and will log the error according to your project's django-logging configuration
        """
        if self.content_type.name == 'node':
            to = [self.to.user.email]
        elif self.content_type.name == 'layer':
            to = [self.to.email]
            # layer case is slightly special, mantainers need to be notified as well
            # TODO: consider making the mantainers able to switch off notifications
            for mantainer in self.to.mantainers.all().only('email'):
                to += [mantainer.email]
        else:
            to = [self.to.email]

        context = {
            'sender_name': self.from_name,
            'sender_email': self.from_email,
            'message': self.message,
            'site': settings.SITE_NAME,
            'object_type': self.content_type.name,
            'object_name': str(self.to)
        }
        message = render_to_string('mailing/inward_message.txt', context)

        email = EmailMessage(
            # subject
            _('Contact request from %(sender_name)s - %(site)s') % context,
            # message
            message,
            # from
            settings.DEFAULT_FROM_EMAIL,
            # to
            to,
            # reply-to header
            headers={'Reply-To': self.from_email}
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
            error_msg = 'nodeshot.community.mailing.models.inward.send(): %s' % e
            log.error(error_msg)
            # set status of the instance as "error"
            self.status = -1

    def save(self, *args, **kwargs):
        """
        Custom save method
        """
        # fill name and email
        if self.user:
            self.from_name = self.user.get_full_name()
            self.from_email = self.user.email

        # if not sent yet
        if int(self.status) < 1:
            # tries sending email (will modify self.status!)
            self.send()

        # save in the database unless logging is explicitly turned off in the settings file
        if INWARD_LOG:
            super(Inward, self).save(*args, **kwargs)
