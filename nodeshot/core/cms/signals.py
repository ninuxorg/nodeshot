from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save
from nodeshot.core.base.cache import cache_delete_pattern_or_all

from .models import Page, MenuItem


@receiver(post_save, sender=Page, dispatch_uid='cms_page_post_save')
@receiver(pre_delete, sender=Page, dispatch_uid='cms_page_pre_delete')
def clear_page_cache(sender, **kwargs):
    cache_delete_pattern_or_all('PageList:*')
    cache_delete_pattern_or_all('PageDetail:*')


@receiver(post_save, sender=MenuItem, dispatch_uid='cms_menuitem_post_save')
@receiver(pre_delete, sender=MenuItem, dispatch_uid='cms_menuitem_pre_delete')
def clear_cache_pages(sender, **kwargs):
    cache_delete_pattern_or_all('MenuList:*')
