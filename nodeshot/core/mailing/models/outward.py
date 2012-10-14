from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.core.mail import EmailMessage
from django.db.models import Q
from nodeshot.core.base.models import BaseDate
from nodeshot.core.nodes.models import Node
from nodeshot.dependencies.fields import MultiSelectField
from choices import *


class Outward(BaseDate):
    """
    This is a tool that can be used to send out newsletters or important communications to your community.
    It's aimed to be useful and flexible.
    """
    status = models.IntegerField(_('status'), choices=OUTWARD_STATUS, default=OUTWARD_STATUS[1][0])
    subject = models.CharField(_('subject'), max_length=50)
    message = models.TextField(_('message'), validators=[
        MinLengthValidator(settings.NODESHOT['SETTINGS']['CONTACT_OUTWARD_MINLENGTH']),
        MaxLengthValidator(settings.NODESHOT['SETTINGS']['CONTACT_OUTWARD_MAXLENGTH'])        
    ])
    is_scheduled = models.SmallIntegerField(_('schedule sending'), choices=SCHEDULE_CHOICES, default=1 if settings.NODESHOT['DEFAULTS']['MAILING_SCHEDULE_OUTWARD'] is True else 0)
    scheduled_date = models.DateField(_('scheduled date'), blank=True, null=True)
    scheduled_time = models.CharField(_('scheduled time'), max_length=20, choices=AVAILABLE_CRONJOBS, default=settings.NODESHOT['DEFAULTS']['CRONJOB'], blank=True)
    is_filtered = models.SmallIntegerField(_('recipient filtering'), choices=FILTERING_CHOICES, default=0)
    filters = MultiSelectField(max_length=255, choices=FILTERS, blank=True, help_text=_('specify recipient filters'))
    groups = MultiSelectField(max_length=255, choices=GROUPS, default=DEFAULT_GROUPS, blank=True, help_text=_('filter specific groups of users'))
    
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
    
    def get_recipients(self):
        """
        Determine recipients depending on:
            * filters
            * groups
            * zones
            * users
        """
        # prepare email list
        emails = []
        
        # send to all case
        if not self.is_filtered:
            # retrieve only email DB column of all active users
            users = User.objects.filter(is_active=True).only('email')
            # loop over users list
            for user in users:
                # add email to the recipient list if not already there
                if not user.email in emails:
                    emails += [user.email]
        else:
            # selected users
            if str(FILTERS[2][0]) in self.filters:
                # retrieve selected users
                users = self.users.all().only('email')
                # loop over selected users
                for user in users:
                    # add email to the recipient list if not already there
                    if not user.email in emails:
                        emails += [user.email]
            
            # Q is a django object for "complex" filtering queries (not that complex in this case)
            # init empty Q object that will be needed in case of group filtering
            q = Q()
            q2 = Q()
            
            # if group filtering is checked
            if str(FILTERS[0][0]) in self.filters:
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
            
            # if zone filtering is checked
            if str(FILTERS[1][0]) in self.filters:
                # retrieve non-external zones
                zones = self.zones.all().only('id')
                # init empty q3
                q3 = Q()
                # loop over zones to form q3 object
                for zone in zones:
                    q3 = q3 | Q(zone=zone)
                # q2: user group if present
                # q3: zones
                # retrieve nodes
                nodes = Node.objects.filter(q2 & q3)
                # loop over nodes of a zone and get their email
                for node in nodes:
                    # add email to the recipient list if not already there
                    if not node.user.email in emails:
                        emails += [node.user.email]

                # loop over selected zones
                #for zone in zones:
                #    nodes = zone.node_set.select_related().filter(q2).only('id', 'user__email')
                #    # loop over nodes of a zone and get their email
                #    for node in nodes:
                #        # add email to the recipient list if not already there
                #        if not node.user.email in emails:
                #            emails += [node.user.email]
            elif str(FILTERS[0][0]) in self.filters and not str(FILTERS[1][0]) in self.filters:
                # TODO: this breaks DRY principle
                # retrieve only email DB column of all active users
                users = User.objects.filter(q).only('email')
                # loop over users list
                for user in users:
                    # add email to the recipient list if not already there
                    if not user.email in emails:
                        emails += [user.email]
            
            
            
        return emails
    
    def send(self):
        """
        Sends the email to the recipients
        """
        # determine recipients
        to = self.get_recipients()
        
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
        
        # add both HTML and plain text support?
        if 'grappelli' in settings.INSTALLED_APPS:
            pass#email.
        
        import socket
        # try sending email
        try:
            email.send()
            self.status = 2
        # if error (connection refused, SMTP down)
        except socket.error as e:
            # log the error
            from logging import error
            error('nodeshot.core.mailing.models.outward.send(): %s' % e)
            # set status of the instance as "error"
            self.status = -1
    
    #def save(self, *args, **kwargs):
    #    """
    #    Custom save method
    #    """
    #    # if not sent yet and is not scheduled to be sent by a cron
    #    if self.status < 2 and not self.is_scheduled:
    #        # tries sending email (will modify self.status!)
    #        self.send()
    #    
    #    super(Outward, self).save(*args, **kwargs)