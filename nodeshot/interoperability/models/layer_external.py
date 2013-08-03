from importlib import import_module

from django.db import models
from django.conf import settings
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
    
    # will hold an instance of the synchronizer class
    _synchronizer = None
    
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
    
    @property
    def synchronizer(self):
        """ access synchronizer """
        if not self.interoperability or not self.layer:
            return False
        
        # init synchronizer if not already done
        if not self._synchronizer:
            interop_module = import_module(self.interoperability)
            # retrieve class name (split and get last piece)
            class_name = self.interoperability.split('.')[-1]
            # retrieve class
            interop_class = getattr(interop_module, class_name)
            self._synchronizer = interop_class(self.layer)
        
        return self._synchronizer
    
    def __init__(self, *args, **kwargs):
        """ custom init method """
        super(LayerExternal, self).__init__(*args, **kwargs)
        
        # if synchronizer has get_nodes method
        # add get_nodes method to current LayerExternal instance
        if self.synchronizer is not False and hasattr(self.synchronizer, 'get_nodes'):
            def get_nodes():
                return self.synchronizer.get_nodes()
            
            self.get_nodes = get_nodes