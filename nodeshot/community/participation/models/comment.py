from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from nodeshot.core.base.models import BaseDate
from nodeshot.core.nodes.models import Node
from nodeshot.community.participation.utils import is_participated
from nodeshot.core.base.models import BaseOrdered
from nodeshot.core.base.managers import AccessLevelManager


class Comment(BaseDate):
    """
    Comment model
    """
    node = models.ForeignKey(Node)
    user = models.ForeignKey(User)
    text = models.CharField(_('comment text'), max_length=255)
    
    # manager
    #objects = AccessLevelManager()
    
    def __unicode__(self):
        return self.text
    
    #Custom save
    #If not exists, creates record for parent node in participation_node_counts table
    def save(self,*args,**kwargs):
        super(Comment,self).save(*args, **kwargs)
        #Check if node is already inserted in participation_node_counts table
        is_participated(self.node.id)
        #Counts node's comments
        node = self.node
        comments = node.comment_set.count()
        #Updates participation_node_counts
        noderatingcount = node.noderatingcount
        noderatingcount.comment_count = comments
        noderatingcount.save()
        
    class Meta:
        app_label='participation'
        #permissions = (('can_view_comment', 'Can view comments'),)
        #ordering = ['order']