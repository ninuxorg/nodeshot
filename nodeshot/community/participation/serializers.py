from rest_framework import serializers,pagination

from django.contrib.auth import get_user_model
User = get_user_model()

from nodeshot.core.nodes.models import Node

from .models import NodeRatingCount, Comment, Vote, Rating


__all__ = [
    'CommentAddSerializer',
    'CommentListSerializer',
    'CommentSerializer',
    'NodeCommentSerializer',
    'ParticipationSerializer',
    'NodeParticipationSerializer',
    'RatingListSerializer',
    'RatingAddSerializer' ,
    'VoteListSerializer',
    'VoteAddSerializer',
    'PaginationSerializer',
    'LinksSerializer',
]


#Pagination serializers

class LinksSerializer(serializers.Serializer):
    
    next = pagination.NextPageField(source='*')
    prev = pagination.PreviousPageField(source='*')


class PaginationSerializer(pagination.BasePaginationSerializer):

    links = LinksSerializer(source='*')  # Takes the page object as the source
    total_results = serializers.Field(source='paginator.count')
    results_field = 'nodes'

#Comments serializers

class CommentAddSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Comment       
        fields= ('node', 'user', 'text', )
    
    
class CommentListSerializer(serializers.ModelSerializer):
    """ Comment serializer """
    node = serializers.Field(source='node.name')
    username = serializers.Field(source='user.username')
    
    class Meta:
        model = Comment
        fields = ('node','username', 'text','added')
        readonly_fields = ('node', 'username', 'added')


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
        
#Rating serializers
        
class RatingAddSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Rating       
        fields= ('node', 'user', 'value', )
    
    
class RatingListSerializer(serializers.ModelSerializer):
    """ Rating serializer """
    node = serializers.Field(source='node.name')
    username = serializers.Field(source='user.username')
    
    class Meta:
        model = Rating
        fields = ('node', 'username', 'value',)
        readonly_fields = ('node', 'username', 'added')

#Vote serializers
        
class VoteAddSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Vote       
        fields= ('node', 'user', 'vote', )
    
    
class VoteListSerializer(serializers.ModelSerializer):
    """ Votes serializer """
    node = serializers.Field(source='node.name')
    username = serializers.Field(source='user.username')
    
    class Meta:
        model = Vote
        fields = ('node', 'username', 'vote',)
        readonly_fields = ('node', 'username', 'added')   

#Participation serializers
 
class ParticipationSerializer(serializers.ModelSerializer):
    
        
    class Meta:
        model = NodeRatingCount
        fields = ('likes', 'dislikes', 'rating_count',
                  'rating_avg', 'comment_count')

    
class NodeParticipationSerializer(serializers.ModelSerializer):
    """ Node participation details"""

    participation = ParticipationSerializer(source='noderatingcount')
    
    class Meta:
        model=Node
        fields= ('name','slug', 'participation')       


