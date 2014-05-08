"""
Notification Registrars are a flexible way to activate notifications for specific models.

Signals are django events on which you can hook your functions.

In this module we define few default registrars, which are simply files
containing directives that register functions to specific django signals,
so it is possible to hook the sending of notifications to certain events like a
node creation or a node deletion, but the key difference is that the execution
of these files, hence the activation of notifications, depends on which registrars
are listed in settings.NODESHOT['NOTIFICATIONS']['REGISTRARS']
"""
