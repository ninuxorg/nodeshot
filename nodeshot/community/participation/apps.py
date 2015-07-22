from django.apps import AppConfig as BaseConfig


class AppConfig(BaseConfig):
    name = 'nodeshot.community.participation'

    def ready(self):
        """ Add user info to ExtensibleNodeSerializer """
        from nodeshot.core.nodes.base import ExtensibleNodeSerializer
        from .models import Vote
        from .serializers import (CommentRelationSerializer,
                                  ParticipationSerializer)

        ExtensibleNodeSerializer.add_relationship(
            'comments',
            serializer=CommentRelationSerializer,
            many=True,
            queryset=lambda obj, request: obj.comment_set.all()
        )

        ExtensibleNodeSerializer.add_relationship(
            'counts',
            serializer=ParticipationSerializer,
            queryset=lambda obj, request: obj.noderatingcount
        )

        ExtensibleNodeSerializer.add_relationship(
            'votes_url',
            view_name='api_node_votes',
            lookup_field='slug'
        )

        ExtensibleNodeSerializer.add_relationship(
            'ratings_url',
            view_name='api_node_ratings',
            lookup_field='slug'
        )

        ExtensibleNodeSerializer.add_relationship(
            'comments_url',
            view_name='api_node_comments',
            lookup_field='slug'
        )

        def voted(obj, request):
            """
            Determines if current logged-in user has already voted on a node
            returns 1 if user has already liked
            returns -1 if user has already disliked
            returns False if user hasn't voted or if not authenticated
            """
            if request.user.is_authenticated():
                v = Vote.objects.filter(node_id=obj.id, user_id=request.user.id)
                if len(v) > 0:
                    return v[0].vote
            # hasn't voted yet or not authenticated
            return False

        ExtensibleNodeSerializer.add_relationship(
            'voted',
            function=voted
        )

        ExtensibleNodeSerializer.add_relationship(
            'voting_allowed',
            function=lambda obj, request: obj.voting_allowed
        )

        ExtensibleNodeSerializer.add_relationship(
            'rating_allowed',
            function=lambda obj, request: obj.rating_allowed
        )

        ExtensibleNodeSerializer.add_relationship(
            'comments_allowed',
            function=lambda obj, request: obj.comments_allowed
        )
