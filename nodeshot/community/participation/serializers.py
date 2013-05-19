from rest_framework import serializers

from django.contrib.auth.models import User

from nodeshot.core.nodes.models import Node

from .models import NodeRatingCount, Comment, Vote, Rating


__all__ = [
    'RatingAddSerializer',
    'VoteAddSerializer',
    'CommentAddSerializer',
    'CommentSerializer',
    'NodeCommentSerializer',
    'ParticipationSerializer',
    'NodeParticipationSerializer'
]


class RatingAddSerializer(serializers.ModelSerializer):
    #node= serializers.Field(source='node.name')
    #username =serializers.Field(source='user.username')
    
    class Meta:
        model = Rating
        #fields = ('username', 'rating')


class VoteAddSerializer(serializers.ModelSerializer):
    #node= serializers.Field(source='node.name')
    #username =serializers.Field(source='user.username')
    
    class Meta:
        model = Vote
        #fields = ('username', 'vote')


class CommentAddSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Comment
        #fields = ('node','username', 'comment')   


class CommentSerializer(serializers.ModelSerializer):
    node= serializers.Field(source='node.name')
    username =serializers.Field(source='user.username')
    
    class Meta:
        model = Comment
        fields = ('username', 'text')


class NodeCommentSerializer(serializers.ModelSerializer):
    
    comments = CommentSerializer(source='comment_set')
    
    class Meta:
        model = Node
        fields = ('name', 'description', 'comments')
        
        
class ParticipationSerializer(serializers.ModelSerializer):
    
    #node= serializers.Field(source='node.name')
    
    class Meta:
        model=NodeRatingCount
        fields= ('likes','dislikes','rating_count','rating_avg','comment_count')

    
class NodeParticipationSerializer(serializers.ModelSerializer):
    """ Node participation details"""

    participation=ParticipationSerializer(source='noderatingcount')
    
    class Meta:
        model=Node
        fields= ('name','participation')       

#class ParticipationSerializer(serializers.ModelSerializer):
#    
#    node= serializers.Field(source='node.name')
#    class Meta:
#        model=NodeRatingCount
#        fields= ('node','likes','dislikes','rating_avg','comment_count')
#
#    
#class ParticipationListSerializer(ParticipationSerializer):
#    """ Node participation details"""
#    details = serializers.HyperlinkedIdentityField(view_name='node_participation_details')
#    class Meta:
#        model=NodeRatingCount
#        fields= ('node','details')
        
#class CommentListSerializer(serializers.ModelSerializer):
#    """ comment_list """
#    node= serializers.Field(source='node.name')
#    user= serializers.Field(source='user.username')
#    class Meta:
#        model=Comment
#        fields= ('node','user','comment')
