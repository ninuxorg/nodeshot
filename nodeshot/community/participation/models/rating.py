from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, Min, Sum, Max, Avg
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.base.models import BaseDate
from nodeshot.core.nodes.models import Node
from nodeshot.community.participation.utils import is_participated


class Rating(BaseDate):
    """
    Rating model
    """
    # rating choices from 1 to 10
    RATING_CHOICES = [(n, '%d' % n) for n in range(1, 11)]
    
    node = models.ForeignKey(Node)
    user = models.ForeignKey(User)
    value = models.IntegerField(_('rating value'), choices=RATING_CHOICES)
    
    def save(self, *args, **kwargs):
        super(Rating,self).save(*args, **kwargs)
        #node_id=self.node
        #a=self.node.id
        is_participated(self.node.id)
        n = self.node
        rating_count = n.rating_set.count()
        rating_avg = n.rating_set.aggregate(rate=Avg('value'))
        rating_float = rating_avg['rate']
        nrc = n.noderatingcount
        nrc.rating_avg = rating_float
        nrc.rating_count = rating_count
        nrc.save()
    
    class Meta:
        app_label='participation'