import django.dispatch

layer_is_published_changed = django.dispatch.Signal(providing_args=["instance", "old_status", "new_status"])
