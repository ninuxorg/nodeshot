from django.contrib.auth import get_user_model
User = get_user_model()

from rest_framework import serializers

from nodeshot.core.base.serializers import ModelValidationSerializer
from nodeshot.community.profiles.serializers import ProfileRelationSerializer

from .models import Comment, Vote, Rating, NodeRatingCount


__all__ = ['CommentSerializer',
           'RatingSerializer',
           'CommentRelationSerializer',
           'VoteSerializer',
           'ParticipationSerializer']


class AutoNodeMixin(object):
    """
    automatically adds node to validated_data
    the node info is taken from views that extend NodeRelationViewMixin
    """
    def validate(self, data):
        data['node'] = self.context['view'].node
        return super(AutoNodeMixin, self).validate(data)


class CommentSerializer(AutoNodeMixin, ModelValidationSerializer):
    """ Comment serializer """
    node = serializers.ReadOnlyField(source='node.name')
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Comment
        fields = ('node', 'username', 'text', 'added')
        read_only_fields = ('added',)


class CommentRelationSerializer(serializers.ModelSerializer):
    """ display user info """
    user = ProfileRelationSerializer()

    class Meta:
        model = Comment
        fields = ('user', 'text', 'added',)


class RatingSerializer(AutoNodeMixin, ModelValidationSerializer):
    """ Rating serializer """
    node = serializers.ReadOnlyField(source='node.name')
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Rating
        fields = ('node', 'username', 'value',)
        read_only_fields = ('added',)


class VoteSerializer(AutoNodeMixin, ModelValidationSerializer):
    node = serializers.ReadOnlyField(source='node.name')
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Vote
        fields = ('node', 'username', 'vote',)
        read_only_fields = ('added',)


class ParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeRatingCount
        fields = ('likes', 'dislikes', 'rating_count',
                  'rating_avg', 'comment_count')
