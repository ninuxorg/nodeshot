from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.base.models import BaseDate
from nodeshot.core.nodes.models import Node

from .base import UpdateCountsMixin


class Vote(UpdateCountsMixin, BaseDate):
    """
    Vote model
    Like or dislike feature
    """
    
    VOTING_CHOICES = (
        (1, 'Like'),
        (-1, 'Dislike'),
    )
    
    node = models.ForeignKey(Node)
    user = models.ForeignKey(User)
    # TODO: this should also be called "value" instead of "vote"
    vote = models.IntegerField(choices=VOTING_CHOICES)
    
    class Meta:
        app_label = 'participation'
    
    def __unicode__(self):
        return self.node.name
    
    def update_count(self):
        """ updates likes and dislikes count """
        node_rating_count = self.node.rating_count
        node_rating_count.likes = self.node.vote_set.filter(vote=1).count()
        node_rating_count.dislikes = self.node.vote_set.filter(vote=-1).count()
        node_rating_count.save()