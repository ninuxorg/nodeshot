from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from nodeshot.core.base.models import BaseDate


class Link(BaseDate):
    """
    External links like website or social network profiles
    """
    user = models.ForeignKey(User, verbose_name=_('user'))
    url = models.URLField(_('url'), verify_exists=True)
    description = models.CharField(_('description'), max_length=128, blank=True)
    
    class Meta:
        db_table = 'profiles_link'
    
    def __unicode__(self):
        return self.url
    
    class Meta:
        app_label= 'profiles'