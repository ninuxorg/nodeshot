from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.base.models import BaseDate
from . import Profile


class SocialLink(BaseDate):
    """
    External links like website or social network profiles
    """
    user = models.ForeignKey(Profile, verbose_name=_('user'))
    url = models.URLField(_('url'))
    description = models.CharField(_('description'), max_length=128, blank=True)

    class Meta:  # NOQA
        ordering = ['id']
        app_label = 'profiles'
        db_table = 'profiles_social_links'
        unique_together = ('user', 'url')

    def __unicode__(self):
        return self.url
