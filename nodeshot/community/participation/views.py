from rest_framework import permissions, authentication, generics
from django.contrib.auth import get_user_model
User = get_user_model()
from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from .models import NodeRatingCount, Rating, Vote, Comment
from serializers import *

from nodeshot.core.nodes.models import Node
from nodeshot.core.layers.models import Layer


def check_node(slug_value):
    """
    Checks if a node exists
    """
    # ensure exists
    try:
        # retrieve slug value from instance attribute kwargs, which is a dictionary
        # get node, ensure is published
        node = Node.objects.published().get(slug=slug_value)
    except Exception:
        raise Http404(_('Node not found'))
    
    return node
        
        
def check_layer(slug_value):
    """
    Checks if a layer exists
    """
    # ensure exists
    try:
        # retrieve slug value from instance attribute kwargs, which is a dictionary
        #slug_value = self.kwargs.get('slug', None)
        # get node, ensure is published
        layer = Layer.objects.published().get(slug=slug_value)
    except Exception:
        raise Http404(_('Layer not found'))
    
    return layer

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
    
    def get(self,request,*args,**kwargs):
        """
        Get comments of specified existing layer
        or otherwise return 404
        """
        # ensure layer exists
        slug_value = self.kwargs.get('slug', None)
        layer = check_layer(slug_value)
        # Get queryset of nodes related to layer
        node = Node.objects.published().all().filter(layer_id=layer.id)        
        self.queryset = node.all()
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
        slug_value = self.kwargs.get('slug', None)
        layer = check_layer(slug_value)
        # Get queryset of nodes related to layer
        node = Node.objects.published().all().filter(layer_id=layer.id)        
        self.queryset = node.all()
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
        self.node = check_node(self.kwargs.get('slug', None))
        
    def pre_save(self, obj):
        """
        Set node id based on the incoming request.
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
        # ensure exists
        slug_value = self.kwargs.get('slug', None)
        check_node(slug_value)
        
        return self.create(request, *args, **kwargs)
    
    def pre_save(self, obj):
        """
        Set node id based on the incoming request.
        """
        slug_value = self.kwargs.get('slug', None)
        node=check_node (slug_value)
        obj.node_id = node.id
    
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
    # ensure exists
        slug_value = self.kwargs.get('slug', None)
        check_node (slug_value)
        return self.create(request, *args, **kwargs)
    
    def pre_save(self, obj):
        """
        Set node id based on the incoming request.
        """
        slug_value = self.kwargs.get('slug', None)
        node = check_node (slug_value)
        obj.node_id = node.id

node_votes = NodeVotesList.as_view()