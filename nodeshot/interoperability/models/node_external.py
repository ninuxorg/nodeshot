import simplejson as json
from importlib import import_module

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from nodeshot.core.nodes.models import Node


class NodeExternal(models.Model):
    """
    External Node info, extend 'Node' with additional data 
    """
    node = models.OneToOneField(Node, verbose_name=_('node'), parent_link=True, related_name='external')
    external_id = models.CharField(_('external id'), blank=True, max_length=255,
                                   help_text=_("""ID of this node on the external layer, might be a hash or an integer
                                               or whatever other format the external application uses to store IDs"""))
    extra_data = models.TextField(_('configuration'), blank=True, help_text=_('JSON format, might contain extra data regarding the external record'))
    
    class Meta:
        db_table = 'nodes_external'
        app_label= 'nodes'
        verbose_name = _('external node')
        verbose_name_plural = _('external node info')

    def __unicode__(self):
        return '%s additional data' % self.node.name

    def clean(self, *args, **kwargs):
        """ Custom Validation """
        
        # extra_data needs to be valid JSON
        if self.extra_data != '' and self.extra_data is not None:
            # convert ' to "
            self.extra_data = self.extra_data.replace("'", '"')
            try:
                extra_data = json.loads(self.extra_data)
            except json.decoder.JSONDecodeError:
                raise ValidationError(_('The specified configuration is not valid JSON'))


# ------ Signals ------ #


from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save


@receiver(post_save, sender=Node)
def save_external_nodes(sender, **kwargs):
    """ sync by creating nodes in external layers when needed """
    
    created = kwargs['created']
    node = kwargs['instance']
    
    if node.layer.is_external is True and node.layer.external.interoperability is not None:
        interop_module = import_module(node.layer.external.interoperability)
        # retrieve class name (split and get last piece)
        class_name = node.layer.external.interoperability.split('.')[-1]
        # retrieve class
        interop_class = getattr(interop_module, class_name)
        
        instance = interop_class(node.layer)
        
        # just check synchronizer has method
        try:
            if created:
                instance.add
            else:
                instance.change
        except AttributeError as e:
            return
        
        if created:
            instance.add(node=node)
        else:
            instance.change(node=node)


@receiver(pre_delete, sender=Node)
def delete_external_nodes(sender, **kwargs):
    """ sync by deleting nodes from external layers when needed """
    
    node = kwargs['instance']
    
    if node.layer.is_external is True and node.layer.external.interoperability is not None:
        interop_module = import_module(node.layer.external.interoperability)
        # retrieve class name (split and get last piece)
        class_name = node.layer.external.interoperability.split('.')[-1]
        # retrieve class
        interop_class = getattr(interop_module, class_name)
        instance = interop_class(node.layer)
        
        # just check method existence
        try:
            instance.delete
        except AttributeError:
            return
        
        # delete
        instance.delete(node=node)