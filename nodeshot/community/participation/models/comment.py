from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.base.models import BaseDate
from nodeshot.core.nodes.models import Node
from nodeshot.community.participation.utils import is_participated


class Comment(BaseDate):
    """
    Comment model
    """
    node = models.ForeignKey(Node)
    user = models.ForeignKey(User)
    text = models.CharField(_('comment text'), max_length=255)
    
    def __unicode__(self):
        return self.comment
    
    def save(self,*args,**kwargs):
        super(Comment,self).save(*args, **kwargs)
        #node_id=self.node
        #a=self.node.id
        is_participated(self.node.id)
        n = self.node
        comments = n.comment_set.count()
        nrc = n.noderatingcount
        nrc.comment_count = comments
        nrc.save()
        
    class Meta:
        app_label='participation'