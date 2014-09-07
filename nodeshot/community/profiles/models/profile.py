from django.db import models
from django.core import validators
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.base.utils import now
from ..settings import settings, EMAIL_CONFIRMATION, REQUIRED_FIELDS as PROFILE_REQUIRED_FIELDS
from ..signals import password_changed

import re


SEX_CHOICES = (
    ('M', _('male')),
    ('F', _('female'))
)


class Profile(AbstractBaseUser, PermissionsMixin):
    """
    User Profile Model
    Contains personal info of a user
    """
    # 254 maximum character for username makes it possible
    username = models.CharField(
        _('username'),
        max_length=254,
        unique=True,
        db_index=True,
        help_text=_('Required. 30 characters or fewer.\
                    Letters, numbers and @/./+/-/_ characters'),
        validators=[
            validators.RegexValidator(
                re.compile('^[\w.@+-]+$'),
                _('Enter a valid username.'),
                'invalid'
            )
        ]
    )
    email = models.EmailField(_('primary email address'), blank=True, unique=True, db_index=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)

    # added fields
    about = models.TextField(_('about me'), blank=True)
    gender = models.CharField(_('gender'), max_length=1, choices=SEX_CHOICES, blank=True)
    birth_date = models.DateField(_('birth date'), blank=True, null=True)
    address = models.CharField(_('address'), max_length=150, blank=True)
    city = models.CharField(_('city'), max_length=30, blank=True)
    country = models.CharField(_('country'), max_length=30, blank=True)

    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether this user should be treated as active.\
                    Unselect this instead of deleting accounts.')
    )
    date_joined = models.DateTimeField(_('date joined'), default=now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = PROFILE_REQUIRED_FIELDS

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        app_label = 'profiles'

    def __unicode__(self):
        return self.username

    def save(self, *args, **kwargs):
        """ ensure instance has usable password when created """
        if not self.pk and self.has_usable_password() is False:
            self.set_password(self.password)

        super(Profile, self).save(*args, **kwargs)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    def add_email(self):
        """
        Add email to DB and sends a confirmation mail if PROFILE_EMAL_CONFIRMATION is True
        """
        if EMAIL_CONFIRMATION:
            from . import EmailAddress
            self.is_active = False
            self.save()
            EmailAddress.objects.add_email(self, self.email)
            return True
        else:
            return False

    def change_password(self, new_password):
        """
        Changes password and sends a signal
        """
        self.set_password(new_password)
        self.save()
        password_changed.send(sender=self.__class__, user=self)

    if 'grappelli' in settings.INSTALLED_APPS:
        @staticmethod
        def autocomplete_search_fields():
            return (
                'username__icontains',
                'first_name__icontains',
                'last_name__icontains',
                'email__icontains'
            )
