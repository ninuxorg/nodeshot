from rest_framework import serializers

from django.contrib.auth import get_user_model
User = get_user_model()

from nodeshot.core.nodes.models import Node

from .models import NodeRatingCount, Comment, Vote, Rating


__all__ = [
    #'CommentAddSerializer',
    'CommentListSerializer',
    'CommentSerializer',
    'NodeCommentSerializer',
    'ParticipationSerializer',
    'NodeParticipationSerializer'
]


#class CommentAddSerializer(serializers.ModelSerializer):
#    
#    class Meta:
#        model = Comment       
#        fields= ('node', 'user', 'text',)
        
        
        
class CommentListSerializer(serializers.ModelSerializer):
    """ Comment serializer """
    node = serializers.Field(source='node.name')
    username = serializers.Field(source='user.username')
    
    class Meta:
        model = Comment
        fields = ('node', 'username', 'text',)
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
        
        
class ParticipationSerializer(serializers.ModelSerializer):
    
        
    class Meta:
        model = NodeRatingCount
        fields = ('likes','dislikes','rating_count','rating_avg','comment_count')

    
class NodeParticipationSerializer(serializers.ModelSerializer):
    """ Node participation details"""

    participation = ParticipationSerializer(source='noderatingcount')
    
    class Meta:
        model=Node
        fields= ('name', 'participation')       


