from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError

from nodeshot.core.base.models import BaseDate

from .base import UpdateCountsMixin


class Vote(UpdateCountsMixin, BaseDate):
    """
    Vote model
    Like or dislike feature
    """

    VOTING_CHOICES = (
        (1, 'Like'),
        (-1, 'Dislike'),
    )

    node = models.ForeignKey('nodes.Node')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    # TODO: this should also be called "value" instead of "vote"
    vote = models.IntegerField(choices=VOTING_CHOICES)

    class Meta:
        app_label = 'participation'

    def __unicode__(self):
        if self.pk:
            return _('vote #%d for node %s') % (self.pk, self.node.name)
        else:
            return _('vote')

    def save(self, *args, **kwargs):
        """
        ensure users cannot vote the same node multiple times
        but let users change their votes
        """
        if not self.pk:
            old_votes = Vote.objects.filter(user=self.user, node=self.node)
            for old_vote in old_votes:
                old_vote.delete()
        super(Vote, self).save(*args, **kwargs)

    def update_count(self):
        """ updates likes and dislikes count """
        node_rating_count = self.node.rating_count
        node_rating_count.likes = self.node.vote_set.filter(vote=1).count()
        node_rating_count.dislikes = self.node.vote_set.filter(vote=-1).count()
        node_rating_count.save()

    def clean(self, *args, **kwargs):
        """
        Check if votes can be inserted for parent node or parent layer
        """
        if not self.pk:
            # ensure voting for this node is allowed
            if self.node.participation_settings.voting_allowed is not True:
                raise ValidationError("Voting not allowed for this node")

            if 'nodeshot.core.layers' in settings.INSTALLED_APPS:
                layer = self.node.layer

                # ensure voting for this layer is allowed
                if layer.participation_settings.voting_allowed is not True:
                    raise ValidationError("Voting not allowed for this layer")
