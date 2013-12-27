import inspect
from importlib import import_module

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.conf import settings

from nodeshot.core.base.models import BaseDate, BaseOrdered
from nodeshot.core.base.managers import HStoreNodeshotManager
from nodeshot.networking.net.models import Device

from django_hstore.fields import DictionaryField


class DeviceConnector(BaseDate, BaseOrdered):
    """
    DeviceConnector Model
    """
    backend = models.CharField(_('backend'), max_length=128,
                              choices=settings.NODESHOT['CONNECTORS'],
                              help_text=_('select the operating system / protocol to use to retrieve info from device'))
    node = models.ForeignKey('nodes.Node', verbose_name=_('node'))
    host = models.CharField(_('host'), max_length=128)
    config = DictionaryField(_('config'), blank=True, null=True,
                            help_text=_('backend specific parameters, eg: username/password (SSH), community (SNMP)'))
    port = models.IntegerField(_('port'), blank=True, null=True,
                               help_text=_('leave blank to use the default port for the protocol in use'))
    store = models.BooleanField(_('store in DB?'),
                                default=True,
                                help_text=_('is adviced to store read-only credentials only'))
    device = models.ForeignKey(Device, verbose_name=_('device'),
                               blank=True, null=True,
                               help_text=_('leave blank, will be created automatically'))
    
    # django manager
    objects = HStoreNodeshotManager()
    
    _connector = None
    _backend_class = None
    
    class Meta:
        ordering = ["order"]
        app_label = 'connectors'
        verbose_name = _('device connector')
        verbose_name_plural = _('device connectors')
    
    def __unicode__(self):
        if self.host:
            return self.host
        else:
            return _(u'Unsaved Device Connector')
    
    def save(self, *args, **kwargs):
        """
        Custom save does the following:
            * start connector class
            * store device if store flag is True
        """
        
        self.host = self.host.strip()
        
        # TODO
        # strip config elements too
        
        #if not self.id:
        #    self.connector.start()
        #    self.device = self.connector.device
        
        if self.store is True:
            super(DeviceConnector, self).save(*args, **kwargs)
    
    def clean(self, *args, **kwargs):
        """
        Call relative connector's clean method
        """
        self._validate_backend()
        self._validate_config()
        self._validate_netengine()
    
    def _validate_backend(self):
        """ ensure backend string representation is correct """
        try:
            self.backend_class
        # if we get an import error the specified path is wrong
        except (ImportError, AttributeError) as e:
            raise ValidationError(_('No valid connector class found, got the following python exception: "%s"') % e)
    
    def _validate_config(self):
        """ ensure REQUIRED_CONFIG_KEYS are filled """
        # exit if no backend specified
        if not self.backend:
            return
        # exit if no required config keys
        if len(self.REQUIRED_CONFIG_KEYS) < 1:
            return
        
        self.config = self.config or {}  # default to empty dict of no config
        required_keys_set = set(self.REQUIRED_CONFIG_KEYS)
        config_keys_set = set(self.config.keys())
        missing_required_keys = required_keys_set - config_keys_set
        
        # if any missing required key raise ValidationError
        if len(missing_required_keys) > 0:
            # converts list in comma separated string
            missing_keys_string = ', '.join(missing_required_keys)
            # django error
            raise ValidationError(_('Missing required config keys: "%s"') % missing_keys_string)
    
    def _validate_netengine(self):
        """
        call netengine instance validate() method
        will verify connection parameters are correct
        """
        if self.backend:
            self.connector.validate()
    
    def _get_netengine_arguments(self, required=False):
        """
        returns list of available config params
        returns list of required config params if required is True
        for internal use only
        """
        # inspect netengine class
        backend_class = self._get_netengine_backend()
        argspec = inspect.getargspec(backend_class.__init__)
        # store args
        args = argspec.args
        # remove known arguments
        for argument_name in ['self', 'host', 'port']:
            args.remove(argument_name)
        
        if required:
            # list of default values
            default_values = list(argspec.defaults)
            # always remove last default value, which is port number
            default_values = default_values[0:-1]
            
            # remove an amount of arguments equals to number of default values, starting from right
            args = args[0:len(args)-len(default_values)]
        
        return args
    
    def _get_netengine_backend(self):
        """
        returns the netengine backend specified in self.backend
        for internal use only
        """
        # extract backend class name, eg: AirOS or OpenWRT
        backend_class_name = self.backend.split('.')[-1]
        # convert to lowercase to get the path
        backend_path = self.backend.lower()
        # import module by its path
        module = import_module(backend_path)
        # get netengine backend class
        BackendClass = getattr(module, backend_class_name)
        
        return BackendClass
    
    def _build_netengine_arguments(self):
        """
        returns a python dictionary representing arguments
        that will be passed to a netengine backend
        for internal use only
        """
        arguments = {
            "host": self.host
        }
        
        if self.config is not None:
            for key, value in self.config.iteritems():
                arguments[key] = value
        
        if self.port:
            arguments["port"] = self.port
        
        return arguments
    
    def get_auto_order_queryset(self):
        """
        Overrides a method of BaseOrdered Abstract Model
        in order to automatically get the order number for last item
        eg: which is the number which represent the last connector regarding to this device?
        """
        return self.__class__.objects.filter(device=self.device)
    
    @property
    def REQUIRED_CONFIG_KEYS(self):
        return self._get_netengine_arguments(required=True)
    
    @property
    def AVAILABLE_CONFIG_KEYS(self):
        return self._get_netengine_arguments()
    
    @property
    def backend_class(self):
        """
        returns python netengine backend class, importing it if needed
        """
        if not self.backend:
            return None
        
        if not self._backend_class:
            self._backend_class = self._get_netengine_backend()
        
        return self._backend_class
    
    @property
    def connector(self):
        """ access connector class """
        # return None if nothing has been chosen yet
        if not self.backend:
            return None
        
        # init instance of the connector class if not already done
        if not self._connector:
            NetengineBackend = self.backend_class
            arguments = self._build_netengine_arguments()
            
            self._connector = NetengineBackend(**arguments)
        
        # return connector instance
        return self._connector


# ------ Extend Device Model with some useful shortcuts related to this module ------ #


#@property
#def connectors(self):
#    """ Nice shortcut to self.deviceconnector_set.all() """ 
#    return self.deviceconnector_set.all()
#
#_connector = False
#
#@property
#def connector(self):
#    """
#    TODO: better explaination
#    Returns the first connector in the order of priority assigned or None if no connector present """
#    # if not retrieved yet
#    if self._connector is False:
#        try:
#            self._connector = self.connectors[0].connector
#        except IndexError:
#            self._connector = None
#    
#    return self._connector
#
#Device.connectors = connectors
#Device._connector = _connector
#Device.connector = connector
#
#Device.extended_by.append('nodeshot.networking.connectors.models.device_connector')
