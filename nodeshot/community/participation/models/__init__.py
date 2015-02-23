from nodeshot.core.base.utils import check_dependencies

check_dependencies(
    dependencies=[
        'nodeshot.core.nodes',
        'nodeshot.community.profiles'
    ],
    module='nodeshot.community.participation'
)

from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from comment import Comment
from vote import Vote
from rating import Rating

from node_participation_settings import NodeParticipationSettings
from node_rating_count import NodeRatingCount


__all__ = [
    'Comment',
    'Vote',
    'Rating',
    'NodeParticipationSettings',
    'NodeRatingCount',
]


# ------ Layers Operations ------ #


if 'nodeshot.core.layers' in settings.INSTALLED_APPS:
    from layer_participation_settings import LayerParticipationSettings

    __all__ += ['LayerParticipationSettings']

    from nodeshot.core.layers.models import Layer

    @property
    def _layer_participation_settings(self):
        """
        Return layer_participation_settings record
        or create it if it does not exist

        usage:
        layer = Layer.objects.get(pk=1)
        layer.participation_settings
        """
        try:
            return self.layer_participation_settings
        except ObjectDoesNotExist:
            layer_participation_settings = LayerParticipationSettings(layer=self)
            layer_participation_settings.save()
            return layer_participation_settings

    Layer.participation_settings = _layer_participation_settings


# ------ Add methods to Node Model ------ #


from nodeshot.core.nodes.models import Node


@property
def _node_rating_count(self):
    """
    Return node_rating_count record
    or create it if it does not exist

    usage:
    node = Node.objects.get(pk=1)
    node.rating_count
    """
    try:
        return self.noderatingcount
    except ObjectDoesNotExist:
        node_rating_count = NodeRatingCount(node=self)
        node_rating_count.save()
        return node_rating_count

Node.rating_count = _node_rating_count


@property
def _node_participation_settings(self):
    """
    Return node_participation_settings record
    or create it if it does not exist

    usage:
    node = Node.objects.get(pk=1)
    node.participation_settings
    """
    try:
        return self.node_participation_settings
    except ObjectDoesNotExist:
        node_participation_settings = NodeParticipationSettings(node=self)
        node_participation_settings.save()
        return node_participation_settings

Node.participation_settings = _node_participation_settings


def _action_allowed(self, action):
    """
    participation actions can be disabled on layer level, or disabled on a per node basis
    """
    if getattr(self.layer.participation_settings, '{0}_allowed'.format(action)) is False:
        return False
    else:
        return getattr(self.participation_settings, '{0}_allowed'.format(action))


@property
def _voting_allowed(self):
    return _action_allowed(self, 'voting')


@property
def _rating_allowed(self):
    return _action_allowed(self, 'rating')


@property
def _comments_allowed(self):
    return _action_allowed(self, 'comments')


Node.voting_allowed = _voting_allowed
Node.rating_allowed = _rating_allowed
Node.comments_allowed = _comments_allowed


# ------ SIGNALS ------ #


from django.dispatch import receiver
from django.db.models.signals import post_save

from ..tasks import create_related_object


@receiver(post_save, sender=Node)
def create_node_rating_counts_settings(sender, **kwargs):
    """ create node rating count and settings"""
    created = kwargs['created']
    node = kwargs['instance']
    if created:
        # create node_rating_count and settings
        # task will be executed in background unless settings.CELERY_ALWAYS_EAGER is True
        # if CELERY_ALWAYS_EAGER is False celery worker must be running otherwise task won't be executed
        create_related_object.delay(NodeRatingCount, {'node': node})
        create_related_object.delay(NodeParticipationSettings, {'node': node})


@receiver(post_save, sender=Layer)
def create_layer_rating_settings(sender, **kwargs):
    """ create layer rating settings """
    created = kwargs['created']
    layer = kwargs['instance']
    if created:
        # create layer participation settings
        # task will be executed in background unless settings.CELERY_ALWAYS_EAGER is True
        # if CELERY_ALWAYS_EAGER is False celery worker must be running otherwise task won't be executed
        create_related_object.delay(LayerParticipationSettings, {'layer': layer})
