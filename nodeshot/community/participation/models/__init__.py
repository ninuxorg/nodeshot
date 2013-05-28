# this app is dependant on "nodes"
from django.conf import settings
if 'nodeshot.core.nodes' not in settings.INSTALLED_APPS:
    from nodeshot.core.base.exceptions import DependencyError
    raise DependencyError('nodeshot.community.participation depends on nodeshot.core.nodes, which should be in settings.INSTALLED_APPS')


from comment import Comment
from vote import Vote
from rating import Rating

from node_participation_settings import NodeParticipationSettings
from node_rating_count import NodeRatingCount

__all__ = [
    'NodeRatingCount',
    'Comment',
    'Vote',
    'Rating',
    'NodeParticipationSettings',
]

if 'nodeshot.core.layers' in settings.INSTALLED_APPS:
    from layer_participation_settings import LayerParticipationSettings
    
    __all__ += ['LayerParticipationSettings']


### SIGNALS ###

from django.dispatch import receiver
from django.db.models.signals import post_save
from nodeshot.core.nodes.models import Node

@receiver(post_save, sender=Node)
def create_node_rating_counts(sender, **kwargs):
    """ create node rating count """
    created = kwargs['created']
    node = kwargs['instance']
    if created:
        # create node_rating_count 
        node_rating_count = NodeRatingCount(node=node)
        node_rating_count.save()