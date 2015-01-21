from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.base.models import BaseOrdered
from nodeshot.core.base.fields import RGBColorField


class Status(BaseOrdered):
    """
    Status of a node, eg: active, potential, approved
    """
    name = models.CharField(_('name'), max_length=255,
                            help_text=_('label for this status, eg: active, approved, proposed'))
    slug = models.SlugField(max_length=75, db_index=True, unique=True)
    description = models.CharField(_('description'), max_length=255,
                                   help_text=_('this description will be used in the legend'))

    is_default = models.BooleanField(
        default=False,
        verbose_name=_('is default status?'),
        help_text=_('indicates whether this is the default status for new nodes;\
                    to change the default status to a new one just check and save,\
                    any other default will be automatically unchecked')
    )

    # map look and feel
    stroke_width = models.SmallIntegerField(
        blank=False,
        default=0,
        help_text=_('stroke of circles shown on map, set to 0 to disable')
    )
    fill_color = RGBColorField(_('fill colour'), blank=True)
    stroke_color = RGBColorField(_('stroke colour'), blank=True, default='#000000')
    text_color = RGBColorField(_('text colour'), blank=True, default='#FFFFFF')

    # needed to intercept changes to is_default
    _current_is_default = False

    class Meta:
        db_table = 'nodes_status'
        app_label = 'nodes'
        verbose_name = _('status')
        verbose_name_plural = _('status')
        ordering = ['order']

    def __unicode__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        """ Fill _current_is_default """
        super(Status, self).__init__(*args, **kwargs)
        # set current is_default, but only if it is an existing status
        if self.pk:
            self._current_is_default = self.is_default

    def save(self, *args, **kwargs):
        """ intercepts changes to is_default """
        ignore_default_check = kwargs.pop('ignore_default_check', False)

        # if making this status the default one
        if self.is_default != self._current_is_default and self.is_default is True:
            # uncheck other default statuses first
            for status in self.__class__.objects.filter(is_default=True):
                status.is_default = False
                status.save(ignore_default_check=True)

        super(Status, self).save(*args, **kwargs)

        # in case there are no default statuses, make this one as the default one
        if self.__class__.objects.filter(is_default=True).count() == 0 and not ignore_default_check:
            self.is_default = True
            self.save()

        # update __current_status
        self._current_is_default = self.is_default
