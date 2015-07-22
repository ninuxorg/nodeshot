from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
User = get_user_model()

from rest_framework import permissions, authentication, generics
from rest_framework.response import Response

from nodeshot.core.nodes.models import Node
from .models import Rating, Vote, Comment
from .serializers import *  # noqa


class NodeRelationViewMixin(object):
    def initial(self, request, *args, **kwargs):
        """
        Custom initial method:
            * ensure node exists and store it in an instance attribute
            * change queryset to return only comments of current node
        """
        super(NodeRelationViewMixin, self).initial(request, *args, **kwargs)
        self.node = get_object_or_404(Node, **{'slug': self.kwargs['slug']})
        self.queryset = self.model.objects.filter(node_id=self.node.id)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NodeComments(NodeRelationViewMixin, generics.ListCreateAPIView):
    """
    ### GET

    Retrieve a **list** of comments for the specified node

    ### POST

    Add a comment to the specified node
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = CommentSerializer
    model = Comment

node_comments = NodeComments.as_view()


class NodeRatings(NodeRelationViewMixin, generics.CreateAPIView):
    """
    ### POST

    Rate the specified node
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = RatingSerializer
    model = Rating

node_ratings = NodeRatings.as_view()


class NodeVotes(NodeRelationViewMixin, generics.CreateAPIView):
    """
    ### POST

    Vote for the specified node
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = VoteSerializer
    model = Vote

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

node_votes = NodeVotes.as_view()
