from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.base.models import BaseDate
from nodeshot.core.nodes.models import Node

from .base import UpdateCountsMixin


class Comment(UpdateCountsMixin, BaseDate):
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