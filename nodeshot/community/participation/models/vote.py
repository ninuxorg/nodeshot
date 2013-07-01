from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError

from nodeshot.core.base.models import BaseDate

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
    
    node = models.ForeignKey('nodes.Node')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
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
   
    #Works for admin but not for API, because pre_save in views.py is executed after this control
    #If uncommented API throws an exception
    
    def clean(self , *args, **kwargs):
        """
        Check if votes can be inserted for parent node or parent layer
        """
        node = self.node
        
        # ensure voting for this node is allowed
        if node.participation_settings.voting_allowed is not True:
            raise ValidationError("Voting not allowed for this node")
        
        if 'nodeshot.core.layers' in settings.INSTALLED_APPS:
            layer = node.layer
            
            # ensure voting for this layer is allowed
            if layer.participation_settings.voting_allowed is not True:
                raise ValidationError("Voting not allowed for this layer")