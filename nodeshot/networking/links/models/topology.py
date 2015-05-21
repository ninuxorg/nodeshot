from collections import OrderedDict

from netdiff import NetJsonParser
from netdiff import diff

from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.module_loading import import_by_path

from nodeshot.core.base.models import BaseDate

from .choices import LINK_STATUS
from ..settings import PARSERS


class Topology(BaseDate):
    name = models.CharField(_('name'), max_length=75, unique=True)
    format = models.CharField(_('format'),
                              choices=PARSERS,
                              max_length=128,
                              help_text=_('Select topology format'))
    url = models.URLField(_('url'), help_text=_('URL where topology will be retrieved'))

    class Meta:
        app_label = 'links'
        verbose_name_plural = _('topologies')

    def __unicode__(self):
        return self.name

    _parser = None

    @property
    def parser(self):
        if not self._parser:
            self._parser = import_by_path(self.format)
        return self._parser

    @property
    def is_layer2(self):
        return self.format == 'netdiff.BatmanParser'

    @property
    def latest(self):
        return self.parser(self.url)

    def diff(self):
        """ shortcut to netdiff.diff """
        current = NetJsonParser(self.json())
        latest = self.latest
        return diff(current, latest)

    def json(self):
        """ returns a dict that represents a NetJSON NetworkGraph object """
        nodes = []
        links = []

        for link in self.link_set.all():
            if self.is_layer2:
                source = link.interface_a.mac
                destination = link.interface_b.mac
            else:
                source = str(link.interface_a.ip_set.first().address)
                destination = str(link.interface_b.ip_set.first().address)
            nodes.append({
                'id': source
            })
            nodes.append({
                'id': destination
            })
            links.append(OrderedDict((
                ('source', source),
                ('target', destination),
                ('weight', link.metric_value)
            )))

        return OrderedDict((
            ('type', 'NetworkGraph'),
            ('protocol', self.parser.protocol),
            ('version', self.parser.version),
            ('metric', self.parser.metric),
            ('nodes', nodes),
            ('links', links)
        ))

    def update(self):
        """
        Updates topology
        Links are not deleted straightaway but set as "disconnected"
        """
        from .link import Link  # avoid circular dependency
        diff = self.diff()

        for link_tuple in diff['added']:
            link = Link.find_or_create(link_tuple)
            changed = False
            if link.status != LINK_STATUS.get('active'):
                link.status = LINK_STATUS.get('active')
                changed = True
            if link.topology != self:
                link.topology = self
                changed = True
            if changed:
                link.save()

        for link_tuple in diff['removed']:
            link = Link.find_or_create(link_tuple)
            changed = False
            if link.status != LINK_STATUS.get('disconnected'):
                link.status = LINK_STATUS.get('disconnected')
                changed = True
            if link.topology != self:
                link.topology = self
                changed = True
            if changed:
                link.save()
