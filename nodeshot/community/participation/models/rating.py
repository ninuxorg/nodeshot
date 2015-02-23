from django.db import models
from django.db.models import Avg
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError

from nodeshot.core.base.models import BaseDate
from nodeshot.core.nodes.models import Node
from nodeshot.core.layers.models import Layer

from .base import UpdateCountsMixin


class Rating(UpdateCountsMixin, BaseDate):
    """
    Rating model
    """
    # rating choices from 1 to 10
    RATING_CHOICES = [(n, '%d' % n) for n in range(1, 11)]

    node = models.ForeignKey(Node)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    value = models.IntegerField(_('rating value'), choices=RATING_CHOICES)

    class Meta:
        app_label = 'participation'

    def __unicode__(self):
        if self.pk:
            return _('rating #%d for node %s') % (self.pk, self.node.name)
        else:
            return _('rating')

    def save(self, *args, **kwargs):
        """
        ensure users cannot rate the same node multiple times
        but let users change their rating
        """
        if not self.pk:
            old_ratings = Rating.objects.filter(user=self.user, node=self.node)
            for old_rating in old_ratings:
                old_rating.delete()
        super(Rating, self).save(*args, **kwargs)

    def update_count(self):
        """ updates rating count and rating average """
        node_rating_count = self.node.rating_count
        node_rating_count.rating_count = self.node.rating_set.count()
        node_rating_count.rating_avg = self.node.rating_set.aggregate(rate=Avg('value'))['rate']

        # if all ratings are deleted the value will be None!
        if node_rating_count.rating_avg is None:
            # set to 0 otherwise we'll get an exception
            node_rating_count.rating_avg = 0

        node_rating_count.save()

    def clean(self, *args, **kwargs):
        """
        Check if rating can be inserted for parent node or parent layer
        """
        if not self.pk:
            node = self.node
            layer = Layer.objects.get(pk=node.layer_id)
            if layer.participation_settings.rating_allowed is not True:
                raise ValidationError("Rating not allowed for this layer")
            if node.participation_settings.rating_allowed is not True:
                raise ValidationError("Rating not allowed for this node")
