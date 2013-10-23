from importlib import import_module

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.conf import settings

from nodeshot.core.base.models import BaseDate


class DeviceLogin(BaseDate):
    """
    DeviceLogin Model
    """
    node = models.ForeignKey('nodes.Node', verbose_name=_('node'))
    host = models.CharField(_('host'), max_length=128)
    username = models.CharField(_('username'), max_length=128)
    password = models.CharField(_('password'), max_length=128)
    port = models.IntegerField(_('port'), default=22)
    store = models.BooleanField(_('store in DB?'),
                                default=False,
                                help_text=_('is adviced to store read-only credentials only'))
    puller_class = models.CharField(_('puller class'), max_length=128,
                              choices=settings.NODESHOT['PULLERS'])
    device = models.ForeignKey('net.Device', verbose_name=_('device'),
                               blank=True, null=True,
                               help_text=_('leave blank, will be created automatically'))
    
    _puller = None
    
    class Meta:
        app_label = 'puller'
        verbose_name = _('device login')
        verbose_name_plural = _('device logins')
    
    def __unicode__(self):
        if self.id:
            return u'%s@%s' % (self.username, self.host)
        else:
            return _(u'Unsaved Device Login')
    
    def clean(self, *args, **kwargs):
        """
        Custom validation
            1.
        """
        pass
    
    def save(self, *args, **kwargs):
        """
        Custom save does the following:
            * start puller class
            * store device if store flag is True
        """
        
        self.host = self.host.strip()
        
        if not self.id:
            self.puller.start()
            self.device = self.puller.device
        
        if self.store is True:
            super(DeviceLogin, self).save(*args, **kwargs)
    
    @property
    def puller(self):
        """ access script class """
        # init puller class if not already done
        if not self._puller:
            script_module = import_module(self.puller_class)
            # retrieve class name (split and get last piece)
            class_name = self.puller_class.split('.')[-1]
            # retrieve class
            ScriptClass = getattr(script_module, class_name)
            self._puller = ScriptClass(self)
        
        return self._puller