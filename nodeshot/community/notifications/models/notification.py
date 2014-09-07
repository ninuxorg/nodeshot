from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext as __
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from nodeshot.core.base.models import BaseDate

from ..settings import settings, TEXTS

NOTIFICATION_TYPE_CHOICES = [(key, _(key)) for key,value in TEXTS.iteritems()]


class Notification(BaseDate):
    """
    Notification Model
    """
    type = models.CharField(_('type'), max_length=64, choices=NOTIFICATION_TYPE_CHOICES)
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  verbose_name=_('from user'),
                                  related_name='notifications_sent',
                                  blank=True, null=True)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                verbose_name=_('to user'),
                                related_name='notifications_received')

    # generic foreign key "related_object" indicates whether the
    # notification refers to any particular object
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    related_object = generic.GenericForeignKey('content_type', 'object_id')

    text = models.CharField(_('text'), max_length=120, blank=True)
    is_read = models. BooleanField(_('read?'), default=False)

    class Meta:
        app_label = 'notifications'
        ordering = ('-id',)

    def __unicode__(self):
        return 'notification #%s' % self.id

    def clean(self, *args, **kwargs):
        """ from_user and to_user must differ """
        if self.from_user and self.from_user_id == self.to_user_id:
            raise ValidationError(_('A user cannot send a notification to herself/himself'))

    def save(self, *args, **kwargs):
        """
        custom save method to send email and push notification
        """
        created = self.pk is None

        # save notification to database only if user settings allow it
        if self.check_user_settings(medium='web'):
            super(Notification, self).save(*args, **kwargs)

        if created:
            # send notifications through other mediums according to user settings
            self.send_notifications()

    def send_notifications(self):
        """ send notifications to recipient user according to her settings """
        self.send_email()

    def send_email(self):
        """ send email notification according to user settings """
        # send only if user notification setting is set to true
        if self.check_user_settings():
            send_mail(_(self.type), self.email_message, settings.DEFAULT_FROM_EMAIL, [self.to_user.email])
            return True
        else:
            # return false otherwise
            return False

    def send_mobile(self):
        """ send push notification according to user settings """
        raise NotImplementedError('mobile notifications not implemented yet')

    def check_user_settings(self, medium='email'):
        """
        Ensure user is ok with receiving this notification through the specified medium.
        Available mediums are 'web' and 'email', while 'mobile' notifications will
        hopefully be implemented in the future.
        """
        # custom notifications are always sent
        if self.type == 'custom':
            return True

        try:
            user_settings = getattr(self.to_user, '%s_notification_settings' % medium)
        except ObjectDoesNotExist:
            # user has no settings specified
            # TODO: it would be better to create the settings with default values
            return False

        user_setting_type = getattr(user_settings.__class__, self.type).user_setting_type

        if user_setting_type == 'boolean':
            return getattr(user_settings, self.type, True)
        elif user_setting_type == 'distance':
            value = getattr(user_settings, self.type, 0)
            # enabled for all related objects
            if value is 0:
                return True
            # disabled for all related objects
            elif value < 0:
                return False
            # enabled for related objects comprised in specified distance range in km
            else:
                Model = self.related_object.__class__
                geo_field = getattr(user_settings.__class__, self.type).geo_field
                geo_value = getattr(self.related_object, geo_field)
                km = value * 1000
                queryset = Model.objects.filter(**{
                    "user_id": self.to_user_id,
                    geo_field+"__distance_lte": (geo_value, km)
                })
                # if user has related object in a distance range less than or equal to
                # his prefered range (specified in number of km), return True and send the notification
                return queryset.count() >= 1

    @property
    def email_message(self):
        """ compose complete email message text """
        url = settings.SITE_URL
        hello_text = __("Hi %s," % self.to_user.get_full_name())
        action_text = __("\n\nMore details here: %s") % url
        explain_text = __(
            "This is an automatic notification sent from from %s.\n"
            "If you want to stop receiving this notification edit your"
            "email notification settings here: %s") % (settings.SITE_NAME, 'TODO')

        return "%s\n\n%s%s\n\n%s" % (hello_text, self.text, action_text, explain_text)
