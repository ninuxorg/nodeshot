from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.core.mail import EmailMessage
from nodeshot.core.base.models import BaseDate
from nodeshot.dependencies.fields import MultiSelectField
from choices import *


class Outward(BaseDate):
    status = models.IntegerField(_('status'), choices=OUTWARD_STATUS, default=OUTWARD_STATUS[1][0])
    subject = models.CharField(_('subject'), max_length=50)
    message = models.TextField(_('message'), validators=[
        MinLengthValidator(settings.NODESHOT['SETTINGS']['CONTACT_OUTWARD_MINLENGTH']),
        MaxLengthValidator(settings.NODESHOT['SETTINGS']['CONTACT_OUTWARD_MAXLENGTH'])        
    ])
    is_scheduled = models.SmallIntegerField(_('schedule sending'), choices=SCHEDULE_CHOICES, default=1 if settings.NODESHOT['DEFAULTS']['MAILING_SCHEDULE_OUTWARD'] is True else 0)
    scheduled_date = models.DateField(_('scheduled date'), blank=True, null=True)
    scheduled_time = models.CharField(_('scheduled time'), max_length=20, choices=AVAILABLE_CRONJOBS, default=settings.NODESHOT['DEFAULTS']['CRONJOB'], blank=True)
    recipient_types = MultiSelectField(max_length=255, blank=True, choices=RECIPIENT_TYPES)
    recipient_groups = MultiSelectField(max_length=255, blank=True, choices=RECIPIENT_GROUPS)
    
    if 'nodeshot.core.zones' in settings.INSTALLED_APPS:
        zones = models.ManyToManyField('zones.Zone', verbose_name=_('zones'), blank=True)
    
    users = models.ManyToManyField(User, verbose_name=_('users'), blank=True)
    
    class Meta:
        verbose_name = _('Outward message')
        verbose_name_plural = _('Outward messages')
        app_label= 'mailing'
        ordering = ['-status']
    
    def __unicode__(self):
        return '%s' % self.subject
    
    def send(self):
        """
        Sends the email to the recipients
        """
        # determine recipients
        to = []
        
        # draft: simplest cases, send to all
        users = User.objects.filter(is_active=True)
        for user in users:
            to += [user.email]
        
        # TODO:
        if self.recipient_types:
            pass
        
        # prepare email object
        email = EmailMessage(
            # subject
            self.subject,
            # message
            self.message,
            # from
            settings.DEFAULT_FROM_EMAIL,
            # to
            to,
        )
        
        import socket
        # try sending email
        try:
            email.send()
            self.status = 2
        # if error
        except socket.error as e:
            # log the error
            from logging import error
            error('nodeshot.core.mailing.models.outward.send(): %s' % e)
            # set status of the instance as "error"
            self.status = -1
    
    def save(self, *args, **kwargs):
        """
        Custom save method
        """
        # if not sent yet and is not scheduled to be sent by a cron
        if self.status < 2 and not self.is_scheduled:
            # tries sending email (will modify self.status!)
            self.send()
        
        super(Outward, self).save(*args, **kwargs)