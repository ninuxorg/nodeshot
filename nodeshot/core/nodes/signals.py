from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save
from django.core.cache import cache

from .models import Node, Status


@receiver(post_save, sender=Node, dispatch_uid='clear_cache_node_saved')
@receiver(pre_delete, sender=Node, dispatch_uid='clear_cache_node_deleted')
@receiver(post_save, sender=Status, dispatch_uid='clear_cache_status_saved')
@receiver(pre_delete, sender=Status, dispatch_uid='clear_cache_status_deleted')
def clear_cache(sender, **kwargs):
    # clear only cached pages if supported
    if hasattr(cache, 'delete_pattern'):
        cache.delete_pattern('views.decorators.cache.cache*')
    # otherwise clear the entire cache
    else:
        cache.clear()
