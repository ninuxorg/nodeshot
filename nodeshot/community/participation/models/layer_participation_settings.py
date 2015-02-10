from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.layers.models import Layer


class LayerParticipationSettings(models.Model):
    """
    Layer settings regarding participation
    """
    layer = models.OneToOneField(Layer, related_name='layer_participation_settings')
    # settings
    voting_allowed = models.BooleanField(_('voting allowed?'), default=True)
    rating_allowed = models.BooleanField(_('rating allowed?'), default=True)
    comments_allowed = models.BooleanField(_('comments allowed?'), default=True)

    def __unicode__(self):
        return self.layer.name

    class Meta:
        app_label = 'participation'
        db_table = 'participation_layer_settings'
        verbose_name_plural = "participation_layer_settings"
