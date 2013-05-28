from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.base.models import BaseDate
from nodeshot.core.nodes.models import Node


class Rating(BaseDate):
    """
    Rating model
    """
    # rating choices from 1 to 10
    RATING_CHOICES = [(n, '%d' % n) for n in range(1, 11)]
    
    node = models.ForeignKey(Node)
    user = models.ForeignKey(User)
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
    
    def save(self, *args, **kwargs):
        """ custom save method to update rating count and rating average """
        # the following lines determines if the comment is being created or not
        # in case the comment exists the pk attribute is an int
        created = type(self.pk) is not int
        
        super(Rating,self).save(*args, **kwargs)
        
        # this operation must be performed after the parent save
        if created:
            self.update_count()
    
    def delete(self, *args, **kwargs):
        """ custom delete method to update rating count and rating average """
        super(Rating, self).delete(*args, **kwargs)
        self.update_count()