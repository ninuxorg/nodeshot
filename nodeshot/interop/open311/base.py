import re

from django.utils.translation import ugettext_lazy as _

from nodeshot.core.nodes.models import Node
from nodeshot.community.participation.models import Vote, Comment, Rating

from .settings import DISCOVERY


SERVICES = {
    'node': {
        'name': _('Node insertion'),
        'description': _('Insert new nodes'),
        'keywords': '',
        'group': ''
    },
    'vote': {
        'name': _('Vote'),
        'description': _('Like or Dislike something'),
        'keywords': '',
        'group': ''
    },
    'comment': {
        'name': _('Comment'),
        'description': _('Leave a comment'),
        'keywords': '',
        'group': ''
    },
    'rate': {
        'name': _('Rate'),
        'description': _('Leave your rating about something'),
        'keywords': '',
        'group': ''
    }
}

MODELS = {
    'node': Node,
    'vote': Vote,
    'comment': Comment,
    'rate': Rating,
}

iso8601_REGEXP = re.compile("^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[0-1]|0[1-9]|[1-2][0-9])?T(2[0-3]|[0-1][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)??(Z|[+-](?:2[0-3]|[0-1][0-9]):[0-5][0-9])?$")
