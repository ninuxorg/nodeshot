import os

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.conf import settings

from nodeshot.core.base.fields import RGBColorField


MARKER_CHOICES = (
    ('icon', _('icon')),
    ('circle', _('coloured circle'))
)

UNIQUE_STATUS_FOREIGN_KEY = 'nodeshot.core.layers' not in settings.INSTALLED_APPS


class StatusIcon(models.Model):
    """
    Icon of a status
    """
    # if layer app is not installed, a status can have only 1 icon
    status = models.ForeignKey('nodes.Status', verbose_name=_('status'), unique=UNIQUE_STATUS_FOREIGN_KEY)
    marker = models.CharField(_('type of marker'), max_length=20, choices=MARKER_CHOICES, help_text=_('icon or simple color?'))
    
    # each layer may have a custom icon for each status
    if 'nodeshot.core.layers' in settings.INSTALLED_APPS:
        layer = models.ForeignKey('layers.Layer', blank=True, null=True,
                help_text=_("""each layer might have its own custom icon,
                            otherwise leave blank to set as default icon for
                            all layers which do not have a custom icon.<br>
                            PS: always be sure there is a default icon."""))
    
    # icon settings
    icon = models.ImageField(upload_to='status-icons/', verbose_name=_('icon of this status'), blank=True, null=True)
    
    # coloured circle settings
    background_color = RGBColorField(_('background colour'), blank=True)
    foreground_color = RGBColorField(_('foreground colour'), blank=True)
    
    class Meta:
        db_table = 'nodes_status_icon'
        app_label= 'nodes'
        
        # if layer app is installed, a status can have 1 custom icon for each layer
        if 'nodeshot.core.layers' in settings.INSTALLED_APPS:
            unique_together = ('status', 'layer')
    
    def __unicode__(self):
        if 'nodeshot.core.layers' in settings.INSTALLED_APPS:
            if self.layer:
                return _('Custom icon of status "%s" for layer "%s"') % (self.status.name, self.layer.name)
            else:
                return _('Default icon of status "%s"') % self.status.name
        else:
            return _('Icon of status "%s"') % self.status.name
    
    def clean(self, *args, **kwargs):
        """
        If marker is an icon ensure an icon image is uploaded;
        If marker is circled ensure a color is chosen;
        There cannot be more than 1 default icon for a status (a default icon is one which does not have any associated layer)
        """
        if self.marker == 'icon' and (self.icon == None or self.icon == ''):
            raise ValidationError(_('icon image is missing'))
        
        if self.marker == 'circle' and (self.background_color == '' or self.foreground_color == ''):
            raise ValidationError(_('circle colour info is missing'))
        
        if not self.pk and 'nodeshot.core.layers' in settings.INSTALLED_APPS and not self.layer:
            if self.__class__.objects.filter(status=self.status, layer=None).count() > 0:
                raise ValidationError(_('Status "%s" already has a default icon' % self.status.name))
    
    def delete(self, *args, **kwargs):
        """ delete image when an image record is deleted """
        if self.icon != None:
            try:
                os.remove(self.icon.file.name)
            # image does not exist
            except (OSError, IOError, ValueError):
                pass
        
        super(StatusIcon, self).delete(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        """ cleanup unnecessary information """
        if self.marker == 'icon':
            self.background_color = ''
            self.foreground_color = ''
        elif self.marker == 'circle':
            self.icon = None
        
        super(StatusIcon, self).save(*args, **kwargs)