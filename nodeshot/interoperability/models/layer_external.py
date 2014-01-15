from importlib import import_module

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError, ImproperlyConfigured

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
    layer = models.OneToOneField('layers.Layer', verbose_name=_('layer'), parent_link=True, related_name='external')
    interoperability = models.CharField(_('interoperability'), max_length=128, choices=INTEROPERABILITY, default=False)
    config = models.TextField(_('configuration'), blank=True,
                              help_text=_('JSON format, will be parsed by the interoperability class to retrieve config keys'))
    map = models.URLField(_('map URL'), blank=True)
    
    # will hold an instance of the synchronizer class
    _synchronizer = None
    _synchronizer_class = None
    
    class Meta:
        app_label = 'interoperability'
        db_table = 'layers_external'
        verbose_name = _('external layer')
        verbose_name_plural = _('external layer info')

    def __unicode__(self):
        return '%s additional data' % self.layer.name

    def clean(self, *args, **kwargs):
        """
        Custom Validation:
        
            * must specify config if interoperability class is not none
            * indent json config nicely
            * validate any synchronizer.REQUIRED_CONFIG_KEYS
            * call synchronizer clean method for any third party validation
        """
        
        # if is interoperable some configuration needs to be specified
        if self.interoperability != 'None' and not self.config:
            raise ValidationError(_('Please specify the necessary configuration for the interoperation'))
        
        # configuration needs to be valid JSON
        if self.interoperability != 'None' and self.config:
            # convert ' to "
            self.config = self.config.replace("'", '"')
            
            # ensure valid JSON
            try:
                config = json.loads(self.config)
            except json.decoder.JSONDecodeError:
                raise ValidationError(_('The specified configuration is not valid JSON'))
            
            # ensure good indentation
            self.config = json.dumps(config, indent=4, sort_keys=True)
            
            # ensure REQUIRED_CONFIG_KEYS are filled
            for key in self.synchronizer_class.REQUIRED_CONFIG_KEYS:
                if key not in config:
                    raise ValidationError(_('Required config key "%s" missing from external layer configuration' % key))
            
            try:
                self.synchronizer.config = config
                self.synchronizer.clean()
            except ImproperlyConfigured as e:
                raise ValidationError(e.message)
    
    def save(self, *args, **kwargs):
        """
        call synchronizer "after_external_layer_saved" method
        for any additional operation that must be executed after save
        """
        after_save = kwargs.pop('after_save', True)
        
        super(LayerExternal, self).save(*args, **kwargs)
        
        if after_save and self.synchronizer:
            self.synchronizer.after_external_layer_saved(self.config)
    
    @property
    def synchronizer(self):
        """ access synchronizer """
        if not self.interoperability or self.interoperability == 'None' or not self.layer:
            return False
        
        # init synchronizer if not already done
        if not self._synchronizer:
            synchronizer_class = self.synchronizer_class
            self._synchronizer = synchronizer_class(self.layer)
        
        return self._synchronizer
    
    @property
    def synchronizer_class(self):
        """ returns synchronizer class """
        if not self.interoperability or self.interoperability == 'None' or not self.layer:
            return False
        
        if not self._synchronizer_class:
            synchronizer_module = import_module(self.interoperability)
            # retrieve class name (split and get last piece)
            class_name = self.interoperability.split('.')[-1]
            # retrieve class
            self._synchronizer_class = getattr(synchronizer_module, class_name)
        
        return self._synchronizer_class
    
    def __init__(self, *args, **kwargs):
        """ custom init method """
        super(LayerExternal, self).__init__(*args, **kwargs)
        
        # avoid blocking page loading in case of missing required config keys in configuration
        try:
            synchronizer = self.synchronizer
        except ImproperlyConfigured:
            return
        
        # if synchronizer has get_nodes method
        # add get_nodes method to current LayerExternal instance
        if synchronizer is not False and hasattr(synchronizer, 'get_nodes'):
            def get_nodes(class_name, params):
                return synchronizer.get_nodes(class_name, params)
            
            self.get_nodes = get_nodes