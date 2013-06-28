"""
interactive shell shortcuts for nodeshot georate project
"""

try:
    from django.contrib.auth.models import AnonymousUser
    from django.contrib.auth import get_user_model
    User = get_user_model()
    from nodeshot.core.nodes.models import Node
    from nodeshot.core.layers.models import Layer
    from nodeshot.community.participation.models import Comment, Rating, Vote
    from nodeshot.community.mailing.models import Outward, Inward
except ImportError as e:
    raise Exception('wrong imports!\n\n%s' % e.message)