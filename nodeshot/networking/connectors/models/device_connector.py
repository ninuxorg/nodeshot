from importlib import import_module

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.conf import settings

from nodeshot.core.base.models import BaseDate, BaseOrdered
from nodeshot.core.base.managers import NodeshotDefaultManager


class DeviceConnector(BaseDate, BaseOrdered):
    """
    DeviceConnector Model
    """
    node = models.ForeignKey('nodes.Node', verbose_name=_('node'))
    host = models.CharField(_('host'), max_length=128)
    username = models.CharField(_('username'), max_length=128, blank=True)
    password = models.CharField(_('password'), max_length=128, blank=True)
    port = models.IntegerField(_('port'), default=22)
    store = models.BooleanField(_('store in DB?'),
                                default=False,
                                help_text=_('is adviced to store read-only credentials only'))
    connector_class = models.CharField(_('connector class'), max_length=128,
                              choices=settings.NODESHOT['CONNECTORS'])
    device = models.ForeignKey('net.Device', verbose_name=_('device'),
                               blank=True, null=True,
                               help_text=_('leave blank, will be created automatically'))
    
    # django manager
    objects = NodeshotDefaultManager()
    
    _connector = None
    
    class Meta:
        ordering = ["order"]
        app_label = 'connectors'
        verbose_name = _('device connector')
        verbose_name_plural = _('device connectors')
    
    def __unicode__(self):
        if self.id:
            return u'%s@%s' % (self.username, self.host)
        else:
            return _(u'Unsaved Device Connector')
    
    def clean(self, *args, **kwargs):
        """
        Call relative connector's clean method
        """
        if self.connector:
            self.connector.clean()
    
    def save(self, *args, **kwargs):
        """
        Custom save does the following:
            * start connector class
            * store device if store flag is True
        """
        
        self.host = self.host.strip()
        
        if not self.id:
            self.connector.start()
            self.device = self.connector.device
        
        if self.store is True:
            super(DeviceConnector, self).save(*args, **kwargs)
    
    def get_auto_order_queryset(self):
        """
        Overrides a method of BaseOrdered Abstract Model
        in order to automatically get the order number for last item
        eg: which is the number which represent the last connector regarding to this device?
        """
        return self.__class__.objects.filter(device=self.device)
    
    @property
    def connector(self):
        """ access connector class """
        # return None if nothing has been chosen yet
        if not self.connector_class:
            return None
        
        # init instance of the connector class if not already done
        if not self._connector:
            script_module = import_module(self.connector_class)
            # retrieve class name (split and get last piece)
            class_name = self.connector_class.split('.')[-1]
            # retrieve class
            ScriptClass = getattr(script_module, class_name)
            self._connector = ScriptClass(self)
        
        # return connector instance
        return self._connector