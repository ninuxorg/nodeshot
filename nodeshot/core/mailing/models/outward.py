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

#class OutwardManager(models.Manager):
#    def send(self):
#            
#        return


class Outward(BaseDate):
    """
    This is a tool that can be used to send out newsletters or important communications to your community.
    It's aimed to be useful and flexible.
    """
    status = models.IntegerField(_('status'), choices=OUTWARD_STATUS_CHOICES, default=OUTWARD_STATUS.get('draft'))
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
        ordering = ['status']
    
    def __unicode__(self):
        return '%s' % self.subject
    
    def get_recipients(self):
        """
        Determine recipients depending on selected filtering which can be either:
            * group based
            * zone based
            * user based
        
        Choosing "group" and "zone" filtering together has the effect of sending the message only to users for which the following conditions are both true:
            * have a node assigned to one of the selected zones
            * are part of any of the specified groups (eg: registered, community, trusted)
            
        The user based filtering has instead the effect of translating in an **OR** query. Here's a practical example:
        if selecting "group" and "user" filtering the message will be sent to all the users for which ANY of the following conditions is true:
            * are part of any of the specified groups (eg: registered, community, trusted)
            * selected users
        """
        # prepare email list
        emails = []
        
        # more human readable stuff
        filters = {
            'groups': str(FILTERS[0][0]),
            'zones': str(FILTERS[1][0]),
            'users': str(FILTERS[2][0])
        }
        
        # the following code is a bit ugly. Considering the titanic amount of work required to build all the cools functionalities that I have in my mind, I can't be bothered to waste time on making it nicer right now.
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
                if not user.email in emails:
                    emails += [user.email]
        else:
            # selected users
            if filters.get('users') in self.filters:
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
            if filters.get('groups') in self.filters:
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
            if filters.get('zones') in self.filters:
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
            # else if group filterins is checked but not zones
            elif filters.get('groups') in self.filters and not filters.get('zones')  in self.filters:
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
        # if it has already been sent don't send again
        if self.status is OUTWARD_STATUS.get('sent'):
            return False
        # determine recipients
        recipients = self.get_recipients()
        # init empty list that will contain django's email objects
        emails = []
        
        # loop over recipients and fill "emails" list
        for recipient in recipients:
            # prepare email object
            emails.append(EmailMessage(
                # subject
                self.subject,
                # message
                self.message,
                # from
                settings.DEFAULT_FROM_EMAIL,
                # to
                [recipient],
            ))
        
        # TODO:
        # add both HTML and plain text support?
        if 'grappelli' in settings.INSTALLED_APPS:
            pass#email.
        
        import socket, time
        # try sending email
        try:
            # counter will count how many emails have been sent
            counter = 0
            for email in emails:
                # if step reached
                if counter == settings.NODESHOT['SETTINGS']['CONTACT_OUTWARD_STEP']:
                    # reset counter
                    counter = 0
                    # sleep
                    time.sleep(settings.NODESHOT['SETTINGS']['CONTACT_OUTWARD_DELAY'])
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
        Besides saving the database record tries to send the email if status is either "error" or "sending"
        """
        # change status to scheduled if necessary
        if self.is_scheduled and self.status is not OUTWARD_STATUS.get('scheduled'):
            self.status = STATUS.get('scheduled')
        # call super.save()
        super(Outward, self).save(*args, **kwargs)