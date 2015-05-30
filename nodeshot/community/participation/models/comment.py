from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from nodeshot.core.base.models import BaseDate
from .base import UpdateCountsMixin


class Comment(UpdateCountsMixin, BaseDate):
    """
    Comment model
    """
    node = models.ForeignKey('nodes.Node')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    text = models.CharField(_('Comment text'), max_length=255)

    class Meta:
        app_label = 'participation'
        db_table = 'participation_comment'
        ordering = ['id']

    def __unicode__(self):
        return self.text

    def update_count(self):
        """ updates comment count """
        node_rating_count = self.node.rating_count
        node_rating_count.comment_count = self.node.comment_set.count()
        node_rating_count.save()

    def clean(self , *args, **kwargs):
        """
        Check if comments can be inserted for parent node or parent layer
        """
        # check done only for new nodes!
        if not self.pk:
            node = self.node

            # ensure comments for this node are allowed
            if  node.participation_settings.comments_allowed is False:
                raise ValidationError("Comments not allowed for this node")

            # ensure comments for this layer are allowed
            if 'nodeshot.core.layers' in settings.INSTALLED_APPS:
                layer = node.layer
                if  layer.participation_settings.comments_allowed is False:
                    raise ValidationError("Comments not allowed for this layer")
