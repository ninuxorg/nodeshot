#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "travis.settings")


if __name__ == "__main__":
    from travis.settings import INSTALLED_APPS
    from django.core.management import execute_from_command_line

    args = sys.argv
    args.insert(1, "test")

    for app in INSTALLED_APPS:
        # include only nodeshot apps
        # exclude connectors because
        if app.startswith('nodeshot.') and app != 'nodeshot.networking.connectors':
            args.append(app)
    
    execute_from_command_line(args)
