"""
interactive shell shortcuts for nodeshot ninux project
"""

try:
    # django
    from django.contrib.auth.models import AnonymousUser
    from django.contrib.auth import get_user_model
    User = get_user_model()
    from django.contrib.gis.measure import D
    # nodeshot
    from nodeshot.core.nodes.models import Node, Image
    from nodeshot.core.layers.models import Layer
    from nodeshot.community.mailing.models import Outward, Inward
except ImportError as e:
    raise Exception('wrong imports!\n\n%s' % e.message)