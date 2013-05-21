from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.nodes.models import Node


class NodeParticipationSettings(models.Model):
    """
    Node Participation Settings
    """
    node = models.OneToOneField(Node)
    # settings
    voting_allowed = models.BooleanField(_('voting allowed?'), default=True)
    rating_allowed = models.BooleanField(_('rating allowed?'), default=True)
    comments_allowed = models.BooleanField(_('comments allowed?'), default=True)

    class Meta:
        app_label='participation'
        db_table='participation_node_settings'
    