from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()

from rest_framework import serializers, pagination

from nodeshot.core.nodes.models import Node
from nodeshot.community.profiles.serializers import ProfileRelationSerializer
from .models import Comment, Vote, Rating, NodeParticipationSettings, NodeRatingCount


__all__ = [
    'CommentAddSerializer',
    'CommentListSerializer',
    'CommentSerializer',
    'NodeCommentSerializer',
    'ParticipationSerializer',
    'NodeParticipationSerializer',
    'RatingListSerializer',
    'RatingAddSerializer',
    'VoteListSerializer',
    'VoteAddSerializer',
    'LinksSerializer',
    'PaginationSerializer',
    'NodeParticipationSettingsSerializer',
    'NodeSettingsSerializer',
    'LayerParticipationSettingsSerializer',
    'LayerSettingsSerializer'
]


class LinksSerializer(serializers.Serializer):
    next = pagination.NextPageField(source='*')
    prev = pagination.PreviousPageField(source='*')


class PaginationSerializer(pagination.BasePaginationSerializer):
    links = LinksSerializer(source='*')  # Takes the page object as the source
    total_results = serializers.Field(source='paginator.count')
    results_field = 'nodes'


class CommentAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('node', 'user', 'text')


class CommentListSerializer(serializers.ModelSerializer):
    """ Comment serializer """
    node = serializers.Field(source='node.name')
    username = serializers.Field(source='user.username')

    class Meta:
        model = Comment
        fields = ('node', 'username', 'text', 'added')
        read_only_fields = ('added',)


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.Field(source='user.username')

    class Meta:
        model = Comment
        fields = ('username', 'text', 'added',)


class NodeCommentSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(source='comment_set')

    class Meta:
        model = Node
        fields = ('name', 'description', 'comments')


class CommentRelationSerializer(serializers.ModelSerializer):
    """ display user info """
    user = ProfileRelationSerializer(source='user')

    class Meta:
        model = Comment
        fields = ('user', 'text', 'added',)


class RatingAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ('node', 'user', 'value', )


class RatingListSerializer(serializers.ModelSerializer):
    """ Rating serializer """
    node = serializers.Field(source='node.name')
    username = serializers.Field(source='user.username')

    class Meta:
        model = Rating
        fields = ('node', 'username', 'value',)
        read_only_fields = ('added',)


class VoteAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ('node', 'user', 'vote', )


class VoteListSerializer(serializers.ModelSerializer):
    """ Votes serializer """
    node = serializers.Field(source='node.name')
    username = serializers.Field(source='user.username')

    class Meta:
        model = Vote
        fields = ('node', 'username', 'vote',)
        read_only_fields = ('added',)


class ParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeRatingCount
        fields = ('likes', 'dislikes', 'rating_count',
                  'rating_avg', 'comment_count')


class NodeParticipationSerializer(serializers.ModelSerializer):
    """ Node participation details """
    participation = ParticipationSerializer(source='noderatingcount')

    class Meta:
        model = Node
        fields = ('name', 'slug', 'address', 'participation')


class NodeSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeParticipationSettings
        fields = ('voting_allowed', 'rating_allowed', 'comments_allowed',)


class NodeParticipationSettingsSerializer(serializers.ModelSerializer):
    """ Node participation settings """
    participation_settings = NodeSettingsSerializer(source='node_participation_settings')

    class Meta:
        model = Node
        fields = ('name', 'slug', 'address', 'participation_settings')


if 'nodeshot.core.layers' in settings.INSTALLED_APPS:
    from .models import LayerParticipationSettings

    class LayerSettingsSerializer(serializers.ModelSerializer):
        class Meta:
            model = LayerParticipationSettings
            fields = ('voting_allowed', 'rating_allowed', 'comments_allowed',)

    # noqa
    class LayerParticipationSettingsSerializer(serializers.ModelSerializer):
        """ Layer participation settings"""
        participation_settings = LayerSettingsSerializer(source='layer_participation_settings')

        class Meta:
            model = Node
            fields = ('name', 'slug', 'participation_settings')


# ------ Add relationship to ExtensibleNodeSerializer ------ #

from nodeshot.core.nodes.serializers import ExtensibleNodeSerializer

ExtensibleNodeSerializer.add_relationship(
    'comments',
    serializer=CommentRelationSerializer,
    many=True,
    queryset=lambda obj, request: obj.comment_set.all()
)

ExtensibleNodeSerializer.add_relationship(
    'counts',
    serializer=ParticipationSerializer,
    queryset=lambda obj, request: obj.noderatingcount
)

ExtensibleNodeSerializer.add_relationship(
    'votes_url',
    view_name='api_node_votes',
    lookup_field='slug'
)

ExtensibleNodeSerializer.add_relationship(
    'ratings_url',
    view_name='api_node_ratings',
    lookup_field='slug'
)

ExtensibleNodeSerializer.add_relationship(
    'comments_url',
    view_name='api_node_comments',
    lookup_field='slug'
)


def voted(obj, request):
    """
    Determines if current logged-in user has already voted on a node
    returns 1 if user has already liked
    returns -1 if user has already disliked
    returns False if user hasn't voted or if not authenticated
    """
    if request.user.is_authenticated():
        v = Vote.objects.filter(node_id=obj.id, user_id=request.user.id)
        if len(v) > 0:
            return v[0].vote
    # hasn't voted yet or not authenticated
    return False

ExtensibleNodeSerializer.add_relationship(
    'voted',
    function=voted
)

ExtensibleNodeSerializer.add_relationship(
    'voting_allowed',
    function=lambda obj, request: obj.voting_allowed
)

ExtensibleNodeSerializer.add_relationship(
    'rating_allowed',
    function=lambda obj, request: obj.rating_allowed
)

ExtensibleNodeSerializer.add_relationship(
    'comments_allowed',
    function=lambda obj, request: obj.comments_allowed
)
