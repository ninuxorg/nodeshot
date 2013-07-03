from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
User = get_user_model()

from rest_framework import permissions, authentication, generics#, exceptions

from .models import NodeRatingCount, Rating, Vote, Comment
from .serializers import *

from nodeshot.core.base.mixins import CustomDataMixin
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


class NodeCommentList(CustomDataMixin, generics.ListCreateAPIView):
    """
    ### GET
    
    Retrieve a **list** of comments for the specified node
    
    ### POST
    
    Add a comment to the specified node
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = CommentListSerializer
    serializer_custom_class = CommentAddSerializer
    
    def get_custom_data(self):
        """ additional request.DATA """
        return {
            'node': self.node.id,
            'user': self.request.user.id
        }
    
    def initial(self, request, *args, **kwargs):
        """
        Custom initial method:
            * ensure node exists and store it in an instance attribute
            * change queryset to return only comments of current node
        """
        super(NodeCommentList, self).initial(request, *args, **kwargs)
        
        # ensure node exists
        self.node = get_queryset_or_404(Node.objects.published(), { 'slug': self.kwargs.get('slug', None) })
        
        # return only comments of current node
        self.queryset = Comment.objects.filter(node_id=self.node.id)
    
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


from django.shortcuts import render
def map_view(request):
    return render(request,'participation/index.html')
