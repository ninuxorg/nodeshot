from .node import Node
from .image import Image
from .status import Status


__all__ = [
    'Node',
    'Image',
    'Status'
]


# ------ Signals ------ #


from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save
from django.core.cache import cache
from ..signals import node_status_changed


@receiver(post_save, sender=Status)
@receiver(pre_delete, sender=Status)
@receiver(post_save, sender=Node)
@receiver(pre_delete, sender=Node)
@receiver(node_status_changed, sender=Node)
def clear_cache(sender, **kwargs):
    # clear only cached pages if supported
    if hasattr(cache, 'delete_pattern'):
        cache.delete_pattern('views.decorators.cache.cache*')
    # otherwise clear the entire cache
    else:
        cache.clear()
