from rest_framework import permissions, authentication, generics
from django.contrib.auth.models import User, Permission
from django.http import Http404
from .models import NodeRatingCount, Rating, Vote, Comment
from serializers import *
from django.utils.translation import ugettext_lazy as _
from nodeshot.core.nodes.models import Node


class CommentCreate(generics.CreateAPIView):
    """
    ### POST
    
    create comments 
    """
    model = Comment
    serializer_class = CommentAddSerializer


class NodeParticipationDetail(generics.RetrieveAPIView):
    """
    ### GET
    
    Retrieve participation details for a node
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    model = Node
    serializer_class= NodeParticipationSerializer
    
node_participation=NodeParticipationDetail.as_view()    
    
class AllNodesParticipationList(generics.ListAPIView):
    """
    ### GET
    
    Retrieve participation details for all nodes
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    model = Node
    serializer_class= NodeParticipationSerializer

all_nodes_participation= AllNodesParticipationList.as_view()
   
class AllNodesCommentList(generics.ListAPIView):
    """
    ### GET
    
    Retrieve comments  for all nodes
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    model = Node
    serializer_class= NodeCommentSerializer
    
all_nodes_comments= AllNodesCommentList.as_view()

class NodeCommentList(generics.ListCreateAPIView):
    """
    ### GET
    
    Retrieve a **list** of comments for the specified node
    
    ### POST
    
    Add a comment for the specified node

    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    model = Comment

    
    def get_queryset(self):
        """
        Get comments of specified existing and published node
        or otherwise return 404
        """
        # ensure exists
        try:
            # retrieve slug value from instance attribute kwargs, which is a dictionary
            slug_value = self.kwargs.get('slug', None)
            # get node, ensure is published
            node = Node.objects.published().get(slug=slug_value)
        except Exception:
            raise Http404(_('Node not found'))
        
        return node.comment_set.all()
    
    
node_comments = NodeCommentList.as_view()    

class NodeRatingList(generics.ListCreateAPIView):
    """
    ### GET
    
    Retrieve a **list** of ratings for the specified node
    
    ### POST
    
    Add a rating for the specified node

    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    model = Rating

    
    def get_queryset(self):
        """
        Get ratings of specified existing and published node
        or otherwise return 404
        """
        # ensure exists
        try:
            # retrieve slug value from instance attribute kwargs, which is a dictionary
            slug_value = self.kwargs.get('slug', None)
            # get node, ensure is published
            node = Node.objects.published().get(slug=slug_value)
        except Exception:
            raise Http404(_('Node not found'))
        
        return node.rating_set.all()
    
    
node_ratings = NodeRatingList.as_view()