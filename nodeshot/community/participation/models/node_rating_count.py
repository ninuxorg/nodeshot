from django.db import models

from nodeshot.core.nodes.models import Node


class NodeRatingCount(models.Model):
    """
    Node Rating Count
    Keep track of participation counts of nodes.
    """
    node = models.OneToOneField(Node)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    rating_count = models.IntegerField(default=0)
    rating_avg = models.FloatField(default=0.0)
    comment_count = models.IntegerField(default=0)
    
    def __unicode__(self):
        return self.node.name
    
    class Meta:
        app_label = 'participation'
        db_table = 'participation_node_counts'