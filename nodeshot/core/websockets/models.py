"""
register websocket signals
"""

from django.conf import settings
from importlib import import_module


for registrar in settings.NODESHOT['WEBSOCKETS']['REGISTRARS']:
    import_module(registrar)