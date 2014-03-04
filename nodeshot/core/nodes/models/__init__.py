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


@receiver(post_save, sender=Status)
@receiver(pre_delete, sender=Status)
def clear_cache(sender, **kwargs):
    cache.clear()