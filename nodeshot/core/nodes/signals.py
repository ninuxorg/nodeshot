import django.dispatch

node_status_changed = django.dispatch.Signal(providing_args=["instance", "old_status", "new_status"])
