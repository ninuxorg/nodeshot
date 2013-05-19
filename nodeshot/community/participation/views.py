from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework import authentication

from .models import NodeRatingCount, Rating, Vote, Comment
from serializers import *

from nodeshot.core.nodes.models import Node


class RatingAdd(generics.CreateAPIView):
    """
    ### POST
    
    Add ratings 
    """
    model = Rating
    serializer_class = RatingAddSerializer
    authentication_classes = (authentication.SessionAuthentication)


class VoteAdd(generics.CreateAPIView):
    """
    ### POST
    
    Add votes 
    """
    model = Vote
    serializer_class= VoteAddSerializer


class CommentAdd(generics.CreateAPIView):
    """
    ### POST
    
    Add comments 
    """
    model = Comment
    serializer_class = CommentAddSerializer


class CommentDetail(generics.RetrieveUpdateAPIView):
    """
    ### POST
    
    Edit comments 
    """
    model = Comment
    serializer_class = CommentAddSerializer


class NodeParticipationDetail(generics.RetrieveAPIView):
    """
    ### GET
    
    Retrieve participation details for a node
    """
    model = Node
    serializer_class= NodeParticipationSerializer
    
    
class NodeParticipationList(generics.ListAPIView):
    """
    ### GET
    
    Retrieve participation details for all nodes
    """
    model = Node
    serializer_class= NodeParticipationSerializer

    
class NodeCommentDetail(generics.RetrieveAPIView):
    """
    ### GET
    
    Retrieve a **list** of comments for a node
    """
    model = Node
    serializer_class= NodeCommentSerializer
    

class NodeCommentList(generics.ListAPIView):
    """
    ### GET
    
    Retrieve a **list** of comments for all nodes
    """
    model = Node
    serializer_class= NodeCommentSerializer

    
#class CommentList(generics.RetrieveAPIView):
#    """
#    ### GET
#    
#    Retrieve a **list** of comments
#    """
#    model= Node
#    serializer_class= NodeParticipationSerializer 

    
#class CommentList(generics.RetrieveAPIView):
#    model= Comment
#    serializer_class= CommentListSerializer