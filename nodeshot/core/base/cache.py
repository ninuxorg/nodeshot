"""
utilities for caching
"""
from django.core.cache import cache


def cache_delete_pattern_or_all(pattern):
    # clear only cached pages if supported
    if hasattr(cache, 'delete_pattern'):
        cache.delete_pattern(pattern)
    # otherwise clear the entire cache
    else:
        cache.clear()


def cache_by_group(view_instance, view_method, request, args, kwargs):
    """
    Cache view response by media type and user group.
    The cache_key is constructed this way: "{view_name:path.group.media_type}"
    EG: "MenuList:/api/v1/menu/.public.application/json"
    Possible groups are:
        * public
        * superuser
        * the rest are retrieved from DB (registered, community, trusted are the default ones)
    """
    if request.user.is_anonymous():
        group = 'public'
    elif request.user.is_superuser:
        group = 'superuser'
    else:
        try:
            group = request.user.groups.all().order_by('-id').first().name
        except IndexError:
            group = 'public'

    key = '%s:%s.%s.%s' % (
        view_instance.__class__.__name__,
        request.META['PATH_INFO'],
        group,
        request.accepted_media_type
    )

    return key
