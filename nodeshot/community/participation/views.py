from rest_framework import permissions, authentication, generics
from django.contrib.auth.models import User, Permission
from django.http import Http404
from .models import NodeRatingCount, Rating, Vote, Comment
from serializers import *
from django.utils.translation import ugettext_lazy as _
from nodeshot.core.nodes.models import Node
from nodeshot.core.layers.models import Layer


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
    
class LayerNodesCommentList(generics.ListAPIView):
    """
    ### GET
    
    Retrieve comments  for all nodes of a layer
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    model = Node
    serializer_class= NodeCommentSerializer
    
    def get_queryset(self):
        """
        Get comments of specified existing layer
        or otherwise return 404
        """
        # ensure exists
        try:
            # retrieve slug value from instance attribute kwargs, which is a dictionary
            slug_value = self.kwargs.get('slug', None)
            # get layer
            layer_id=Layer.objects.get(slug=slug_value)
            node=Node.objects.published().all().filter(layer_id=layer_id)

            #node = Node.objects.published().get(layer_id=1)
        except Exception:
            raise Http404(_('Node not found'))
        
        return node.all()
    
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
    
    def get_queryset(self):
        """
        Get comments of specified existing layer
        or otherwise return 404
        """
        # ensure exists
        try:
            # retrieve slug value from instance attribute kwargs, which is a dictionary
            slug_value = self.kwargs.get('slug', None)
            # get layer
            layer_id=Layer.objects.get(slug=slug_value)
            node=Node.objects.published().all().filter(layer_id=layer_id)

            #node = Node.objects.published().get(layer_id=1)
        except Exception:
            raise Http404(_('Node not found'))
        
        return node.all()
    
layer_nodes_participation= LayerNodesParticipationList.as_view()

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
    #serializer_class=CommentAddSerializer
    
    def get(self, request, *args, **kwargs):
        self.serializer_class = CommentListSerializer
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        self.serializer_class = CommentAddSerializer
        # ensure exists
        try:
            # retrieve slug value from instance attribute kwargs, which is a dictionary
            slug_value = self.kwargs.get('slug', None)
            # get node, ensure is published
            node = Node.objects.published().get(slug=slug_value)
        except Exception:
            raise Http404(_('Node not found'))
        
        #request.DATA['node'] = node.id
        #data = request.DATA.copy()
        #data['node'] = node.id
        #request.DATA = data
        
        return self.create(request, *args, **kwargs)
    
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
        try:
            # retrieve slug value from instance attribute kwargs, which is a dictionary
            slug_value = self.kwargs.get('slug', None)
            # get node, ensure is published
            node = Node.objects.published().get(slug=slug_value)
        except Exception:
            raise Http404(_('Node not found'))
        return self.create(request, *args, **kwargs)
    
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
        try:
            # retrieve slug value from instance attribute kwargs, which is a dictionary
            slug_value = self.kwargs.get('slug', None)
            # get node, ensure is published
            node = Node.objects.published().get(slug=slug_value)
        except Exception:
            raise Http404(_('Node not found'))
        return self.create(request, *args, **kwargs)
    
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
        
        return node.vote_set.all()
    
    
node_votes = NodeVotesList.as_view()