import simplejson as json

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError, ImproperlyConfigured, ObjectDoesNotExist
from django.utils.module_loading import import_by_path

from django_hstore.fields import DictionaryField

from ..settings import SYNCHRONIZERS


# choices
SYNCHRONIZERS = [
    ('None', _('None'))
] + SYNCHRONIZERS


class LayerExternal(models.Model):
    """
    External Layers, extend 'Layers' with additional files
    These are the layers that are managed by local groups or other organizations
    """
    layer = models.OneToOneField('layers.Layer', verbose_name=_('layer'), parent_link=True, related_name='external')
    synchronizer_path = models.CharField(_('synchronizer'), max_length=128, choices=SYNCHRONIZERS, default=False)
    config = DictionaryField(_('configuration'),
                             blank=True,
                             null=True,
                             help_text=_('Synchronizer specific configuration (eg: API URL, auth info, ecc)'))
    field_mapping = DictionaryField(_('field mapping'),
                                    blank=True,
                                    null=True,
                                    help_text=_('Map nodeshot field names to the field names used by the external application'))

    # will hold an instance of the synchronizer class
    _synchronizer = None
    _synchronizer_class = None

    class Meta:
        app_label = 'sync'
        db_table = 'layers_external'
        verbose_name = _('external layer')
        verbose_name_plural = _('external layer info')

    def __unicode__(self):
        try:
            return '%s external layer config' % self.layer.name
        except ObjectDoesNotExist:
            return 'LayerExternal object'

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
            self.get_nodes = synchronizer.get_nodes

    def clean(self, *args, **kwargs):
        """
        Custom Validation:
            * must specify config if synchronizer_path is not 'None'
            * indent json config nicely
            * validate any synchronizer.REQUIRED_CONFIG_KEYS
            * call synchronizer clean method for any third party validation
        """
        # if is interoperable some configuration needs to be specified
        if self.synchronizer_path != 'None' and not self.config:
            raise ValidationError(_('Please specify the necessary configuration for the interoperation'))
        # configuration needs to be valid JSON
        if self.synchronizer_path != 'None' and self.config:
            # ensure REQUIRED_CONFIG_KEYS are filled
            for key in self.synchronizer_class.REQUIRED_CONFIG_KEYS:
                if key not in self.config:
                    raise ValidationError(_('Required config key "%s" missing from external layer configuration' % key))
            # validate synchronizer config
            try:
                self.synchronizer.load_config(self.config)
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
        # call after_external_layer_saved method of synchronizer
        if after_save and self.synchronizer:
            self.synchronizer.after_external_layer_saved(self.config)

    @property
    def synchronizer(self):
        """ access synchronizer """
        if not self.synchronizer_path or self.synchronizer_path == 'None' or not self.layer:
            return False
        # ensure data is up to date
        if (self._synchronizer is not None and self._synchronizer_class.__name__ not in self.synchronizer_path):
            self._synchronizer = None
            self._synchronizer_class = None
        # init synchronizer only if necessary
        if not self._synchronizer:
            self._synchronizer = self.synchronizer_class(self.layer)
        return self._synchronizer

    @property
    def synchronizer_class(self):
        """ returns synchronizer class """
        if not self.synchronizer_path or self.synchronizer_path == 'None' or not self.layer:
            return False
        # ensure data is up to date
        if (self._synchronizer_class is not None and self._synchronizer_class.__name__ not in self.synchronizer_path):
            self._synchronizer = None
            self._synchronizer_class = None
        # import synchronizer class only if not imported already
        if not self._synchronizer_class:
            self._synchronizer_class = import_by_path(self.synchronizer_path)
        return self._synchronizer_class
