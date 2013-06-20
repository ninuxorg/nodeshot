from rest_framework import permissions, authentication, generics
from django.contrib.auth.models import User, Permission
from django.http import Http404
from django.shortcuts import render
from .models import NodeRatingCount, Rating, Vote, Comment
from serializers import *
from django.utils.translation import ugettext_lazy as _
from nodeshot.core.nodes.models import Node
from nodeshot.core.layers.models import Layer


def get_queryset_or_404(queryset, kwargs):
    """
    Checks if object returned by queryset exists
    """
    # ensure exists
    try:
        obj = queryset.get(**kwargs)
    except Exception:
        raise Http404(_('Not found'))
    
    return obj
        
        
#def check_layer(slug_value):
#    """
#    Checks if a layer exists
#    """
#    # ensure exists
#    try:
#        # retrieve slug value from instance attribute kwargs, which is a dictionary
#        #slug_value = self.kwargs.get('slug', None)
#        # get node, ensure is published
#        layer = Layer.objects.published().get(slug=slug_value)
#    except Exception:
#        raise Http404(_('Layer not found'))
#    
#    return layer

#class CommentCreate(generics.CreateAPIView):
#    """
#    ### POST
#    
#    create comments 
#    """
#    model = Comment
#    serializer_class = CommentAddSerializer
    
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

 
class LayerNodesCommentList(generics.ListAPIView):
    """
    ### GET
    
    Retrieve comments  for all nodes of a layer
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    model = Node
    serializer_class= NodeCommentSerializer
    
    def get(self, request, *args, **kwargs):
        """
        Get comments of specified existing layer
        or otherwise return 404
        """
        # ensure layer exists
        layer = get_queryset_or_404(Layer.objects.published(), { 'slug': self.kwargs.get('slug', None) })
        
        # Get queryset of nodes related to layer
        self.queryset = Node.objects.published().filter(layer_id=layer.id)
        
        return self.list(request, *args, **kwargs)

layer_nodes_comments= LayerNodesCommentList.as_view()


class LayerNodesParticipationList(generics.ListAPIView):
    """
    ### GET
    
    Retrieve participation details for all nodes of a layer
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    model = Node
    serializer_class= NodeParticipationSerializer
    
    def get(self,request,*args,**kwargs):
        """
        Get comments of specified existing layer
        or otherwise return 404
        """
        # ensure layer exists
        layer = get_queryset_or_404(Layer.objects.published(), { 'slug': self.kwargs.get('slug', None) })
        
        # Get queryset of nodes related to layer
        self.queryset = Node.objects.published().filter(layer_id=layer.id)
        
        return self.list(request, *args, **kwargs)
    
layer_nodes_participation= LayerNodesParticipationList.as_view()


class NodeParticipationDetail(generics.RetrieveAPIView):
    """
    ### GET
    
    Retrieve participation details for a node
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    model = Node
    serializer_class = NodeParticipationSerializer
    
node_participation = NodeParticipationDetail.as_view()  


class NodeCommentList(generics.ListCreateAPIView):
    """
    ### GET
    
    Retrieve a **list** of comments for the specified node
    
    ### POST
    
    Add a comment to the specified node
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    model = Comment
    serializer_class = CommentListSerializer
    
    def initial(self, request, *args, **kwargs):
        """ overwritten initial method to ensure node exists """
        super(NodeCommentList, self).initial(request, *args, **kwargs)
        # ensure node exists
        self.node = get_queryset_or_404(Node.objects.published(), { 'slug': self.kwargs.get('slug', None) })
        
    def pre_save(self, obj):
        """
        Set node and user id based on the incoming request.
        """
        obj.node_id = self.node.id
        obj.user_id = self.request.user.id
    
node_comments = NodeCommentList.as_view()    


class NodeRatingList(generics.CreateAPIView):
    """
    ### POST
    
    Add a rating for the specified node
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    model = Rating
    
    def post(self, request, *args, **kwargs):
        # ensure node exists
        self.node = get_queryset_or_404(Node.objects.published(), { 'slug': self.kwargs.get('slug', None) })
        
        return self.create(request, *args, **kwargs)
    
    def pre_save(self, obj):
        """
        Set node and user id based on the incoming request.
        """
        obj.node_id = self.node.id
        obj.user_id = self.request.user.id
    
node_ratings = NodeRatingList.as_view()

class NodeVotesList(generics.CreateAPIView):
    """
    
    ### POST
    
    Add a vote for the specified node

    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    model = Vote
    
    def post(self, request, *args, **kwargs):
        # ensure node exists
        self.node = get_queryset_or_404(Node.objects.published(), { 'slug': self.kwargs.get('slug', None) })
        
        return self.create(request, *args, **kwargs)
    
    def pre_save(self, obj):
        """
        Set node and user id based on the incoming request.
        """
        obj.node_id = self.node.id
        obj.user_id = self.request.user.id

node_votes = NodeVotesList.as_view()