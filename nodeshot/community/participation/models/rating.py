from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from django.db.models import Avg
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from nodeshot.core.base.models import BaseDate
from nodeshot.core.nodes.models import Node

from .base import UpdateCountsMixin


class Rating(UpdateCountsMixin, BaseDate):
    """
    Rating model
    """
    # rating choices from 1 to 10
    RATING_CHOICES = [(n, '%d' % n) for n in range(1, 11)]
    
    node = models.ForeignKey(Node)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    value = models.IntegerField(_('rating value'), choices=RATING_CHOICES)
    
    class Meta:
        app_label = 'participation'
    
    def update_count(self):
        """ updates rating count and rating average """
        node_rating_count = self.node.rating_count
        node_rating_count.rating_count = self.node.rating_set.count()
        node_rating_count.rating_avg = self.node.rating_set.aggregate(rate=Avg('value'))['rate']
        
        # if all ratings are deleted the value will be None!
        if node_rating_count.rating_avg is None:
            # set to 0 otherwise we'll get an exception
            node_rating_count.rating_avg = 0

        node_rating_count.save()
