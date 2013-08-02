from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

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
    is_published = models.BooleanField(default=True)
    
    objects = AccessLevelPublishedManager()
    
    def __unicode__(self):
        return self.url