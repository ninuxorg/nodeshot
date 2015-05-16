from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.base.models import BaseDate

from ..settings import PARSERS


class Topology(BaseDate):
    name = models.CharField(_('name'), max_length=75, unique=True)
    format = models.CharField(_('format'), max_length=128,
                                            choices=PARSERS,
                                            help_text=_('Select topology format'))
    url = models.URLField(_('url'), help_text=_('URL where topology will be retrieved'))

    class Meta:
        app_label = 'links'
        verbose_name_plural = _('topologies')

    def __unicode__(self):
        return self.name
