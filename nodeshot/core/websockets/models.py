"""
register websocket signals
"""

from importlib import import_module
from .settings import REGISTER


for module in REGISTER:
    import_module(module)
