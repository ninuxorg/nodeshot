import socket
import time

from django.db import models
from django.db.models import Q
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.utils.translation import ugettext_lazy as _
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model

from nodeshot.core.base.models import BaseDate
from nodeshot.core.base.fields import MultiSelectField
from nodeshot.core.base.utils import now
from nodeshot.core.nodes.models import Node

from .choices import *  # noqa
from ..settings import settings, OUTWARD_SCHEDULING, OUTWARD_MINLENGTH, OUTWARD_MAXLENGTH, OUTWARD_HTML, OUTWARD_STEP, OUTWARD_DELAY


class Outward(BaseDate):
    """
    This is a tool that can be used to send out newsletters or important communications to your community.
    It's aimed to be useful and flexible.
    """
    status = models.IntegerField(_('status'), choices=OUTWARD_STATUS_CHOICES,
                                 default=OUTWARD_STATUS.get('draft'))
    subject = models.CharField(_('subject'), max_length=50)
    message = models.TextField(_('message'), validators=[
        MinLengthValidator(OUTWARD_MINLENGTH),
        MaxLengthValidator(OUTWARD_MAXLENGTH)
    ])
    is_scheduled = models.SmallIntegerField(_('schedule sending'),
                                            choices=SCHEDULE_CHOICES,
                                            default=0)
    scheduled_date = models.DateField(_('scheduled date'), blank=True, null=True)
    scheduled_time = models.CharField(_('scheduled time'), max_length=20,
                                      choices=OUTWARD_SCHEDULING,
                                      default=OUTWARD_SCHEDULING[0][0],
                                      blank=True)
    is_filtered = models.SmallIntegerField(_('recipient filtering'),
                                           choices=FILTERING_CHOICES,
                                           default=0)
    filters = MultiSelectField(max_length=255, choices=FILTER_CHOICES,
                               blank=True,
                               help_text=_('specify recipient filters'))
    groups = MultiSelectField(max_length=255, choices=GROUPS,
                              default=DEFAULT_GROUPS,
                              blank=True,
                              help_text=_('filter specific groups of users'))

    if 'nodeshot.core.layers' in settings.INSTALLED_APPS:
        layers = models.ManyToManyField('layers.Layer', verbose_name=_('layers'), blank=True)

    users = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_('users'), blank=True)

    class Meta:
        verbose_name = _('Outward message')
        verbose_name_plural = _('Outward messages')
        app_label = 'mailing'
        ordering = ['status']

    def __unicode__(self):
        return '%s' % self.subject

    def get_recipients(self):
        """
        Determine recipients depending on selected filtering which can be either:
            * group based
            * layer based
            * user based

        Choosing "group" and "layer" filtering together has the effect of sending the message
        only to users for which the following conditions are both true:
            * have a node assigned to one of the selected layers
            * are part of any of the specified groups (eg: registered, community, trusted)

        The user based filtering has instead the effect of translating in an **OR** query. Here's a practical example:
        if selecting "group" and "user" filtering the message will be sent to all the users for which ANY of the following conditions is true:
            * are part of any of the specified groups (eg: registered, community, trusted)
            * selected users
        """
        # user model
        User = get_user_model()

        # prepare email list
        emails = []

        # the following code is a bit ugly. Considering the titanic amount of work required to build all
        # the cools functionalities that I have in my mind, I can't be bothered to waste time on making it nicer right now.
        # if you have ideas on how to improve it to make it cleaner and less cluttered, please join in
        # this method has unit tests written for it, therefore if you try to change it be sure to check unit tests do not fail after your changes
        # python manage.py test mailing

        # send to all case
        if not self.is_filtered:
            # retrieve only email DB column of all active users
            users = User.objects.filter(is_active=True).only('email')
            # loop over users list
            for user in users:
                # add email to the recipient list if not already there
                if user.email not in emails:
                    emails += [user.email]
        else:
            # selected users
            if FILTERS.get('users') in self.filters:
                # retrieve selected users
                users = self.users.all().only('email')
                # loop over selected users
                for user in users:
                    # add email to the recipient list if not already there
                    if user.email not in emails:
                        emails += [user.email]

            # Q is a django object for "complex" filtering queries (not that complex in this case)
            # init empty Q object that will be needed in case of group filtering
            q = Q()
            q2 = Q()

            # if group filtering is checked
            if FILTERS.get('groups') in self.filters:
                # loop over each group
                for group in self.groups:
                    # if not superusers
                    if group != '0':
                        # add the group to the Q object
                        # this means that the query will look for users of that specific group
                        q = q | Q(groups=int(group))
                        q2 = q2 | Q(user__groups=int(group))
                    else:
                        # this must be done manually because superusers is not a group but an attribute of the User model
                        q = q | Q(is_superuser=True)
                        q2 = q2 | Q(user__is_superuser=True)

            # plus users must be active
            q = q & Q(is_active=True)

            # if layer filtering is checked
            if FILTERS.get('layers') in self.filters:
                # retrieve non-external layers
                layers = self.layers.all().only('id')
                # init empty q3
                q3 = Q()
                # loop over layers to form q3 object
                for layer in layers:
                    q3 = q3 | Q(layer=layer)
                # q2: user group if present
                # q3: layers
                # retrieve nodes
                nodes = Node.objects.filter(q2 & q3)
                # loop over nodes of a layer and get their email
                for node in nodes:
                    # add email to the recipient list if not already there
                    if node.user.email not in emails:
                        emails += [node.user.email]
            # else if group filterins is checked but not layers
            elif FILTERS.get('groups') in self.filters and not FILTERS.get('layers') in self.filters:
                # retrieve only email DB column of all active users
                users = User.objects.filter(q).only('email')
                # loop over users list
                for user in users:
                    # add email to the recipient list if not already there
                    if user.email not in emails:
                        emails += [user.email]
        return emails

    def send(self):
        """
        Sends the email to the recipients
        """
        # if it has already been sent don't send again
        if self.status is OUTWARD_STATUS.get('sent'):
            return False
        # determine recipients
        recipients = self.get_recipients()
        # init empty list that will contain django's email objects
        emails = []

        # prepare text plain if necessary
        if OUTWARD_HTML:
            # store plain text in var
            html_content = self.message
            # set EmailClass to EmailMultiAlternatives
            EmailClass = EmailMultiAlternatives
        else:
            EmailClass = EmailMessage

        # default message is plain text
        message = strip_tags(self.message)

        # loop over recipients and fill "emails" list
        for recipient in recipients:
            msg = EmailClass(
                # subject
                self.subject,
                # message
                message,
                # from
                settings.DEFAULT_FROM_EMAIL,
                # to
                [recipient],
            )
            if OUTWARD_HTML:
                msg.attach_alternative(html_content, "text/html")
            # prepare email object
            emails.append(msg)

        # try sending email
        try:
            # counter will count how many emails have been sent
            counter = 0
            for email in emails:
                # if step reached
                if counter == OUTWARD_STEP:
                    # reset counter
                    counter = 0
                    # sleep
                    time.sleep(OUTWARD_DELAY)
                # send email
                email.send()
                # increase counter
                counter += 1
        # if error (connection refused, SMTP down)
        except socket.error as e:
            # log the error
            from logging import error
            error('nodeshot.core.mailing.models.outward.send(): %s' % e)
            # set status of the instance as "error"
            self.status = OUTWARD_STATUS.get('error')
        # change status
        self.status = OUTWARD_STATUS.get('sent')
        # save
        self.save()

    def save(self, *args, **kwargs):
        """
        Custom save method
        """
        # change status to scheduled if necessary
        if self.is_scheduled and self.status is not OUTWARD_STATUS.get('scheduled'):
            self.status = OUTWARD_STATUS.get('scheduled')

        # call super.save()
        super(Outward, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        """
        Custom validation
        """
        if self.is_scheduled is 1 and (self.scheduled_date == '' or self.scheduled_date is None
                                       or self.scheduled_time == '' or self.scheduled_time is None):
            raise ValidationError(_('If message is scheduled both fields "scheduled date" and "scheduled time" must be specified'))

        if self.is_scheduled is 1 and self.scheduled_date < now().date():
            raise ValidationError(_('The scheduled date is set to a past date'))

        if self.is_filtered is 1 and (len(self.filters) < 1 or self.filters == [''] or
                                      self.filters == [u''] or self.filters == '' or self.filters is None):
            raise ValidationError(_('If "recipient filtering" is active one of the filtering options should be selected'))

        if self.is_filtered is 1 and FILTERS.get('groups') in self.filters and\
           (len(self.groups) < 1 or self.groups == [''] or self.groups == [u''] or self.groups == '' or self.groups is None):
            raise ValidationError(_('If group filtering is active at least one group of users should be selected'))

        # TODO: unfortunately layers and users can't be validated easily because they are a many2many field
