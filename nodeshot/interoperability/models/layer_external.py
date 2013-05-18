from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from nodeshot.core.layers.models import Layer

import simplejson as json


# choices
INTEROPERABILITY = [
    ('None', _('Not interoperable'))
] + settings.NODESHOT['INTEROPERABILITY']


class LayerExternal(models.Model):
    """
    External Layers, extend 'Layers' with additional files
    These are the layers that are managed by local groups or other organizations
    """
    layer = models.OneToOneField(Layer, verbose_name=_('layer'), parent_link=True, related_name='external')
    interoperability = models.CharField(_('interoperability'), max_length=128, choices=INTEROPERABILITY, default=False)
    config = models.TextField(_('configuration'), blank=True, help_text=_('JSON format, will be parsed by the interoperability class to retrieve config keys'))
    map = models.URLField(_('map URL'), blank=True)
    
    class Meta:
        db_table = 'layers_external'
        app_label= 'layers'
        verbose_name = _('external layer')
        verbose_name_plural = _('external layer info')

    def __unicode__(self):
        return '%s additional data' % self.layer.name

    def clean(self, *args, **kwargs):
        """ Custom Validation """
        
        # if is interoperable some configuration needs to be specified
        if self.interoperability != 'None' and not self.config:
            raise ValidationError(_('Please specify the necessary configuration for the interoperation'))
        
        # configuration needs to be valid JSON
        if self.interoperability != 'None' and self.config:
            # convert ' to "
            self.config = self.config.replace("'", '"')
            try:
                config = json.loads(self.config)
            except json.decoder.JSONDecodeError:
                raise ValidationError(_('The specified configuration is not valid JSON'))