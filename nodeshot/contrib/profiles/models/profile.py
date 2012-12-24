from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from nodeshot.core.base.models import BaseDate
from choices import SEX_CHOICES


class Profile(BaseDate):
    """
    User Profile Model
    Contains the personal info of a user
    """
    user = models.OneToOneField(User, verbose_name=_('user'))
    gender = models.CharField(_('gender'), max_length=1, choices=SEX_CHOICES, blank=True)
    birth_date = models.DateField(_('birth date'), blank=True, null=True)
    city = models.CharField(_('city'), max_length=30, blank=True)
    about = models.TextField(_('about me'), blank=True)
    
    def __unicode__(self):
        return self.user.username
    
    class Meta:
        app_label= 'profiles'
        permissions = (('can_view_profiles', 'Can view profiles'),)