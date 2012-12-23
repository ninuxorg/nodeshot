from django.utils.translation import ugettext_lazy as _
from nodeshot.core.base.utils import choicify


NODE_STATUS = {
    'archived': -1,
    'potential': 0,
    'planned': 1,
    'testing': 2,
    'active': 3,
    'mantainance': 4,
}

NODE_STATUS_CHOICES = choicify(NODE_STATUS)