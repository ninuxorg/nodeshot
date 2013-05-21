import django.dispatch

node_status_changed = django.dispatch.Signal(providing_args=["old_status", "new_status"])