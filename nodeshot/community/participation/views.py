from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
User = get_user_model()

from rest_framework import permissions, authentication, generics
from rest_framework.response import Response

from .models import Rating, Vote, Comment
from .serializers import *  # noqa

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
    Retrieve participation details for all nodes
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    model = Node
    serializer_class = NodeParticipationSerializer
    pagination_serializer_class = PaginationSerializer
    paginate_by_param = 'limit'
    paginate_by = 10

all_nodes_participation = AllNodesParticipationList.as_view()


class AllNodesCommentList(generics.ListAPIView):
    """
    Retrieve comments  for all nodes
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    model = Node
    serializer_class = NodeCommentSerializer
    pagination_serializer_class = PaginationSerializer
    paginate_by_param = 'limit'
    paginate_by = 10

all_nodes_comments = AllNodesCommentList.as_view()


class LayerNodesCommentList(generics.ListAPIView):
    """
    Retrieve comments  for all nodes of a layer
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    model = Node
    serializer_class = NodeCommentSerializer

    def get(self, request, *args, **kwargs):
        """
        Get comments of specified existing layer
        or otherwise return 404
        """
        # ensure layer exists
        layer = get_queryset_or_404(Layer.objects.published(), {'slug': self.kwargs.get('slug', None)})

        # Get queryset of nodes related to layer
        self.queryset = Node.objects.published().filter(layer_id=layer.id)

        return self.list(request, *args, **kwargs)

layer_nodes_comments = LayerNodesCommentList.as_view()


class LayerNodesParticipationList(generics.ListAPIView):
    """
    Retrieve participation details for all nodes of a layer
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    model = Node
    serializer_class = NodeParticipationSerializer

    def get(self, request, *args, **kwargs):
        """
        Get comments of specified existing layer
        or otherwise return 404
        """
        # ensure layer exists
        layer = get_queryset_or_404(Layer.objects.published(), {'slug': self.kwargs.get('slug', None)})
        # Get queryset of nodes related to layer
        self.queryset = Node.objects.published().filter(layer_id=layer.id)
        return self.list(request, *args, **kwargs)

layer_nodes_participation = LayerNodesParticipationList.as_view()


class NodeParticipationDetail(generics.RetrieveAPIView):
    """
    Retrieve participation details for a node
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    model = Node
    serializer_class = NodeParticipationSerializer

node_participation = NodeParticipationDetail.as_view()


class NodeParticipationSettingsDetail(generics.RetrieveAPIView):
    """
    Retrieve participation settings for a node
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    model = Node
    serializer_class = NodeParticipationSettingsSerializer

node_participation_settings = NodeParticipationSettingsDetail.as_view()


class LayerParticipationSettingsDetail(generics.RetrieveAPIView):
    """
    Retrieve participation settings for a layer
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    model = Layer
    serializer_class = LayerParticipationSettingsSerializer

layer_participation_settings = LayerParticipationSettingsDetail.as_view()


class NodeCommentList(CustomDataMixin, generics.ListCreateAPIView):
    """
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
        self.node = get_queryset_or_404(Node.objects.published(), {'slug': self.kwargs.get('slug', None)})
        # return only comments of current node
        self.queryset = Comment.objects.filter(node_id=self.node.id)

node_comments = NodeCommentList.as_view()


class NodeRatingList(CustomDataMixin, generics.CreateAPIView):
    """
    Not allowed

    ### POST

    Add a rating for the specified node
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = RatingListSerializer
    serializer_custom_class = RatingAddSerializer

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
        super(NodeRatingList, self).initial(request, *args, **kwargs)
        # ensure node exists
        self.node = get_queryset_or_404(Node.objects.published(), {'slug': self.kwargs.get('slug', None)})
        # return only comments of current node
        self.queryset = Rating.objects.filter(node_id=self.node.id)

node_ratings = NodeRatingList.as_view()


class NodeVotesList(CustomDataMixin, generics.CreateAPIView):
    """
    Add a vote for the specified node
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = VoteListSerializer
    serializer_custom_class = VoteAddSerializer

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
        super(NodeVotesList, self).initial(request, *args, **kwargs)
        # ensure node exists
        self.node = get_queryset_or_404(Node.objects.published(), {'slug': self.kwargs.get('slug', None)})
        # return only comments of current node
        self.queryset = Vote.objects.filter(node_id=self.node.id)

    def delete(self, *args, **kwargs):
        votes = Vote.objects.filter(node_id=self.node.id, user_id=self.request.user.id)
        if (len(votes) > 0):
            for vote in votes:
                vote.delete()
            message = _('Vote for this node removed')
            status = 200
        else:
            message = _('User has not voted this node yet')
            status = 400
        return Response({'details': message}, status=status)

node_votes = NodeVotesList.as_view()
