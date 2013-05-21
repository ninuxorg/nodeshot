from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.layers.models import Layer


class LayerParticipationSettings(models.Model):
    """
    Layer settings regarding participation
    """
    layer = models.OneToOneField(Layer)
    # settings
    voting_allowed = models.BooleanField(_('voting allowed?'), default=True)
    rating_allowed = models.BooleanField(_('rating allowed?'), default=True)
    comments_allowed = models.BooleanField(_('comments allowed?'), default=True)

    class Meta:
        db_table='participation_layer_settings'
        app_label='layers'
    