from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.base.models import BaseDate


class SocialLink(BaseDate):
    """
    External links like website or social network profiles
    """
    user = models.ForeignKey(User, verbose_name=_('user'))
    url = models.URLField(_('url'))
    description = models.CharField(_('description'), max_length=128, blank=True)
    
    class Meta:
        db_table = 'profiles_social_links'
    
    def __unicode__(self):
        return self.url
    
    class Meta:
        app_label= 'profiles'