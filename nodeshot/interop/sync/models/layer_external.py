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
    synchronizer_path = models.CharField(_('synchronizer'), max_length=128, choices=SYNCHRONIZERS, default='None')
    config = DictionaryField(_('configuration'),
                             help_text=_('Synchronizer specific configuration (eg: API URL, auth info, ecc)'),
                             blank=True,
                             null=True,
                             editable=False,
                             schema=None)
    # private attributes that will hold synchronizer info
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
            synchronizer = False
        # if synchronizer has get_nodes method
        # add get_nodes method to current LayerExternal instance
        if synchronizer is not False and hasattr(synchronizer, 'get_nodes'):
            self.get_nodes = synchronizer.get_nodes
        # load schema
        self._reload_schema()

    def _reload_schema(self):
        if self.synchronizer_class:
            schema = self.synchronizer_class.SCHEMA
        else:
            schema = None
        if self.config.field.schema is not schema:
            self.config.field.reload_schema(schema)
            # if schema is None set editable to False
            if schema is None:
                self.config.field.editable = False

    def clean(self, *args, **kwargs):
        """
        Call self.synchronizer.clean method
        """
        if self.synchronizer_path != 'None' and self.config:
            # call synchronizer custom clean
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
        if after_save:
            try:
                synchronizer = self.synchronizer
            except ImproperlyConfigured:
                pass
            else:
                if synchronizer:
                    synchronizer.after_external_layer_saved(self.config)
        # reload schema
        self._reload_schema()

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
            self._synchronizer = (self.synchronizer_class)(self.layer)
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
