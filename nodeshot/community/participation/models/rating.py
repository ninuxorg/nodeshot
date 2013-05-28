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
    
    #Custom save
    def save(self, *args, **kwargs):
        super(Rating,self).save(*args, **kwargs)
        # If not exists, inserts node in participation_node_counts
        is_participated(self.node.id)
        #Counts node's ratings
        node= self.node
        rating_count = node.rating_set.count()
        rating_avg = node.rating_set.aggregate(rate=Avg('value'))
        rating_float = rating_avg['rate']
        #Updates participation_node_counts
        noderatingcount = node.noderatingcount
        noderatingcount.rating_avg = rating_float
        noderatingcount.rating_count = rating_count
        noderatingcount.save()
    
    class Meta:
        app_label='participation'