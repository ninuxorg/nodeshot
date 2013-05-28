from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.base.models import BaseDate
from nodeshot.core.nodes.models import Node


class Comment(BaseDate):
    """
    Comment model
    """
    node = models.ForeignKey(Node)
    user = models.ForeignKey(User)
    text = models.CharField(_('Comment text'), max_length=255)
    
    class Meta:
        app_label = 'participation'
    
    def __unicode__(self):
        return self.text
    
    def update_count(self):
        """ updates comment count """
        node_rating_count = self.node.rating_count
        node_rating_count.comment_count = self.node.comment_set.count()
        node_rating_count.save()
    
    def save(self, *args, **kwargs):
        """ custom save method to update comments count """
        # the following lines determines if the comment is being created or not
        # in case the comment exists the pk attribute is an int
        created = type(self.pk) is not int
        
        super(Comment, self).save(*args, **kwargs)
        
        # this operation must be performed after the parent save
        if created:
            self.update_count()
    
    def delete(self, *args, **kwargs):
        """ custom delete method to update comments count """
        super(Comment, self).delete(*args, **kwargs)
        self.update_count()