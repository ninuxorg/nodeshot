from .node import Node
from .image import Image
from .status import Status
from .status_icon import StatusIcon


__all__ = [
    'Node',
    'Image',
    'Status',
    'StatusIcon'
]


# ------ Signals ------ #


from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save
from django.core.cache import cache


@receiver(post_save, sender=Status)
@receiver(post_save, sender=StatusIcon)
@receiver(pre_delete, sender=Status)
@receiver(pre_delete, sender=StatusIcon)
def clear_cache(sender, **kwargs):
    cache.clear()