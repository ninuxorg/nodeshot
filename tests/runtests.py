#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ci.settings")


if __name__ == "__main__":
    args = sys.argv
    args.insert(1, "test")
    args.insert(2, "--noinput")
    from ci.settings import INSTALLED_APPS
    from django.core.management import execute_from_command_line

    for app in INSTALLED_APPS:
        # include only nodeshot apps
        if app == 'nodeshot.ui.default':
            args.append('{0}.tests.DefaultUiDjangoTest'.format(app))
        elif app.startswith('nodeshot.'):
            args.append(app)

    execute_from_command_line(args)
