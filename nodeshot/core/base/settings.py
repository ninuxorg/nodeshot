from django.conf import settings

ACCESS_LEVELS = getattr(settings, 'NODESHOT_ACCESS_LEVELS', {
    'registered': 1,
    'community': 2,
    'trusted': 3
})
ACL_DEFAULT_VALUE = getattr(settings, 'NODESHOT_ACL_DEFAULT_VALUE', 'public')
ACL_DEFAULT_EDITABLE  = getattr(settings, 'NODESHOT_ACL_DEFAULT_EDITABLE', True)
DISCONNECTABLE_SIGNALS = getattr(settings, 'NODESHOT_DISCONNECTABLE_SIGNALS', [])
