import datetime
from random import random
from hashlib import sha1

from django.db import models, IntegrityError
from django.core.mail import send_mail
from django.core.urlresolvers import reverse, NoReverseMatch
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from ..signals import email_confirmed, email_confirmation_sent
from ..settings import settings

try:
    from django.utils.timezone import now
except ImportError:
    now = datetime.datetime.now


__all__ = [
    'EmailAddress',
    'EmailConfirmation'
]


class EmailAddressManager(models.Manager):
    def add_email(self, user, email):
        try:
            email_address = self.create(user=user, email=email)
            EmailConfirmation.objects.send_confirmation(email_address)
            return email_address
        except IntegrityError:
            return None

    def get_primary(self, user=None):
        # if we're a related_manager, use the User object we're attached to
        inst = getattr(self, 'instance', None)
        if not user and not inst:
            raise ValueError("Must specify a User")
        if user and inst and user != inst:
            raise ValueError("Cannot specify a different User")
        user = user or inst

        try:
            return self.get(user=user, primary=True)
        except EmailAddress.DoesNotExist:
            return None

    def get_users_for(self, email):
        """
        returns a list of users with the given email.
        """
        # this is a list rather than a generator because we probably want to
        # do a len() on it right away
        return [address.user for address in EmailAddress.objects.filter(verified=True, email=email)]


class EmailAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='email_set')
    email = models.EmailField(unique=True)
    verified = models.BooleanField(default=False)
    primary = models.BooleanField(default=False)

    objects = EmailAddressManager()

    def clean(self):
        try:
            if self.pk and not self.primary and self.user.email_set.get_primary().pk == self.pk:
                raise ValidationError(_("You must have at least one primary email address."))
        except IndexError:
            pass

    def save(self, *args, **kwargs):
        set_as_primary = False
        # if primary is True and this is not the only primary email address for this user
        if self.primary and self.user.email_set.filter(primary=True).exclude(pk=self.pk).count() > 0:
            set_as_primary = True
        # if primary is not true but no primary email addresses for this user
        if not self.primary and self.user.email_set.filter(primary=True).count() < 1:
            set_as_primary = True
        # if adding a new primary address from the admin
        if not self.pk and self.primary:
            set_as_primary = True
        super(EmailAddress, self).save(*args, **kwargs)
        if set_as_primary:
            # ensure there's only 1 primary address
            self.set_as_primary()

    def set_as_primary(self):
        old_primaries = self.user.email_set.filter(primary=True).exclude(pk=self.pk)
        for old_primary in old_primaries:
            old_primary.primary = False
            old_primary.save()
        self.primary = True
        self.save()

        self.user.email = self.email
        update_fields = ['email']
        if getattr(settings, 'EMAIL_CONFIRMATION_OVERWRITE_USERNAME', False):
            self.user.username = self.email
            update_fields.append('username')
        try:
            # django 1.5+
            # necessary because of more aggresive related model caching
            self.user.save(update_fields=update_fields)
        except TypeError:
            self.user.save()

        return True

    def __unicode__(self):
        return u"%s (%s)" % (self.email, self.user)

    class Meta:
        ordering = ['-primary', 'id']
        app_label = 'profiles'
        verbose_name = _("email address")
        verbose_name_plural = _("email addresses")
        unique_together = (
            ("user", "email"),
        )


class EmailConfirmationManager(models.Manager):
    def generate_key(self, email):
        """
        Generate a new email confirmation key and return it.
        """
        salt = sha1(str(random())).hexdigest()[:5]
        return sha1(salt + email).hexdigest()

    def create_emailconfirmation(self, email_address):
        "Create an email confirmation obj from the given email address obj"
        confirmation_key = self.generate_key(email_address.email)
        confirmation = self.create(
            email_address=email_address,
            created_at=now(),
            key=confirmation_key,
        )
        return confirmation

    def confirm_email(self, key, user=None, make_primary=True):
        queryset = self.all()
        if user:
            queryset = queryset.filter(email_address__user=user)
        try:
            confirmation = queryset.get(key=key)
        except self.model.DoesNotExist:
            return None
        if not confirmation.key_expired():
            email_address = confirmation.email_address
            email_address.verified = True
            if make_primary:
                email_address.set_as_primary()
            email_address.save()
            email_confirmed.send(sender=self.model, email_address=email_address)
            return email_address

    def send_confirmation(self, email_address):
        confirmation = self.create_emailconfirmation(email_address)
        # check for the url with the dotted view path
        try:
            path = reverse("emailconfirmation.views.confirm_email", args=[confirmation.key])
        except NoReverseMatch:
            # or get path with named urlconf instead
            path = reverse("emailconfirmation_confirm_email", args=[confirmation.key])
        activate_url = u"%s%s" % (settings.SITE_URL, path)
        context = {
            "user": email_address.user,
            "activate_url": activate_url,
            "site_name": settings.SITE_NAME,
            "confirmation_key": confirmation.key,
        }
        subject = render_to_string("profiles/email_messages/email_confirmation_subject.txt", context)
        # remove superfluous line breaks
        subject = "".join(subject.splitlines())
        message = render_to_string("profiles/email_messages/email_confirmation_message.txt", context)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email_address.email])

        email_confirmation_sent.send(sender=self.model, confirmation=confirmation)
        return confirmation

    def delete_expired_confirmations(self):
        for confirmation in self.all():
            if confirmation.key_expired():
                confirmation.delete()


class EmailConfirmation(models.Model):
    email_address = models.ForeignKey(EmailAddress)
    created_at = models.DateTimeField()
    key = models.CharField(max_length=40)

    objects = EmailConfirmationManager()

    def key_expired(self):
        confirmation_days = getattr(settings, 'EMAIL_CONFIRMATION_DAYS', 7)
        expiration_date = self.created_at + datetime.timedelta(days=confirmation_days)
        return expiration_date <= timezone.now()
    key_expired.boolean = True

    def __unicode__(self):
        return u"confirmation for %s" % self.email_address

    class Meta:
        app_label = 'profiles'
        verbose_name = _("email confirmation")
        verbose_name_plural = _("email confirmations")
