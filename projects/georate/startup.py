"""
interactive shell shortcuts for nodeshot georate project
"""

try:
    from django.contrib.auth.models import User
    from nodeshot.core.nodes.models import Node
    from nodeshot.core.layers.models import Layer
    from nodeshot.community.mailing.models import Outward, Inward
except ImportError as e:
    raise Exception('wrong imports!\n\n%s' % e.message)