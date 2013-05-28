from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.base.models import BaseDate
from nodeshot.core.nodes.models import Node
from nodeshot.community.participation.utils import is_participated


class Vote(BaseDate):
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
    vote = models.IntegerField(choices=VOTING_CHOICES)
    
    def __unicode__(self):
        return self.node.name
    #Custom save
    def save(self, *args, **kwargs):
        super(Vote,self).save(*args, **kwargs)
        # If not exists, inserts node in participation_node_counts
        is_participated(self.node.id)
        #Counts node's votes
        node = self.node
        likes = node.vote_set.filter(vote=1).count()
        dislikes = node.vote_set.filter(vote=-1).count()
        #Updates participation_node_counts
        noderatingcount = n.noderatingcount
        noderatingcount.likes = likes
        noderatingcount.dislikes = dislikes
        noderatingcount.save()
    
    class Meta:
        app_label = 'participation'