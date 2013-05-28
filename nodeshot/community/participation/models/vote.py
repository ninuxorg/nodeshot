from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.base.models import BaseDate
from nodeshot.core.nodes.models import Node


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
    
    def save(self, *args, **kwargs):
        """ custom save method to update likes and dislikes count """
        # the following lines determines if the comment is being created or not
        # in case the comment exists the pk attribute is an int
        created = type(self.pk) is not int
        
        super(Vote,self).save(*args, **kwargs)
        
        # this operation must be performed after the parent save
        if created:
            self.update_count()
    
    def delete(self, *args, **kwargs):
        """ custom delete method to update likes and dislikes count """
        super(Vote, self).delete(*args, **kwargs)
        self.update_count()