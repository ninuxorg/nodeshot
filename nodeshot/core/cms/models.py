from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from nodeshot.core.base.models import BaseAccessLevel, BaseOrderedACL
from nodeshot.core.base.managers import AccessLevelPublishedManager


__all__ = ['Page', 'MenuItem']


ROBOTS_CHOICES = (
    ('index, follow', 'index, follow'),
    ('noindex, follow', 'noindex, follow'),
    ('index, nofollow', 'index, nofollow'),
    ('noindex, nofollow', 'noindex, nofollow'),
)


class Page(BaseAccessLevel):
    """
    Page Model
    """
    title = models.CharField(_('title'), max_length=50)
    slug = models.SlugField(_('slug'), max_length=50, blank=True, unique=True)
    content = models.TextField(_('content'))
    is_published = models.BooleanField(default=True)

    # meta fields, optional
    meta_description = models.CharField(_('meta description'), max_length=255, blank=True)
    meta_keywords = models.CharField(_('meta keywords'), max_length=255, blank=True)
    meta_robots = models.CharField(max_length=50, choices=ROBOTS_CHOICES, default=ROBOTS_CHOICES[0][0])

    objects = AccessLevelPublishedManager()

    def __unicode__(self):
        return self.title


class MenuItem(BaseOrderedACL):
    """
    MenuItem Model
    """
    name = models.CharField(_('name'), max_length=50)
    url = models.CharField(_('url'), max_length=255)
    classes = models.CharField(_('classes'), max_length=50, blank=True, help_text=_('space separated css classes'))
    parent = models.ForeignKey('self', blank=True, null=True)
    is_published = models.BooleanField(default=True)

    objects = AccessLevelPublishedManager()

    def __unicode__(self):
        return self.name

    def clean(self):
        """ support only 1 level of nesting """
        if self.parent is not None and self.parent.parent is not None:
            raise ValidationError(_('1 level of nesting only is supported'))


# ------ Signals ------ #


from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save
from nodeshot.core.base.cache import cache_delete_pattern_or_all


@receiver(post_save, sender=Page)
@receiver(pre_delete, sender=Page)
def clear_page_cache(sender, **kwargs):
    cache_delete_pattern_or_all('PageList:*')
    cache_delete_pattern_or_all('PageDetail:*')

@receiver(post_save, sender=MenuItem)
@receiver(pre_delete, sender=MenuItem)
def clear_cache_pages(sender, **kwargs):
    cache_delete_pattern_or_all('MenuList:*')
