from datetime import datetime

from django.contrib.gis.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _

from jsonfield import JSONField

from nodeshot.core.base.models import BaseDate

from . import settings as local_settings
from .utils import get_db


class Metric(BaseDate):
    name = models.CharField(_('name'), max_length=75)
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    related_object = generic.GenericForeignKey('content_type', 'object_id')
    tags = JSONField(_('tags'), blank=True, default={})
    retention_policy = models.CharField(_('retention policy'),
                                        max_length=32,
                                        choices=local_settings.RETENTION_POLICIES,
                                        default=local_settings.DEFAULT_RETENTION_POLICY)

    class Meta:
        unique_together = ('name', 'content_type', 'object_id')

    def __init__(self, *args, **kwargs):
        self.db = get_db()
        super(Metric, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.related_object:
            self.tags.update({
                'content_type': self.content_type.name,
                'object_id': str(self.object_id)
            })
        super(Metric, self).save(*args, **kwargs)

    def write(self, fields, timestamp=None, database=None):
        """ write metric point """
        if timestamp is not None and isinstance(timestamp, datetime):
            timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
        return self.db.write({
            'database': database or local_settings.INFLUXDB_DATABASE,
            'retentionPolicy': 'policy_{0}'.format(local_settings.DEFAULT_RETENTION_POLICY),
            'points': [
                {
                    'name': self.name,
                    'tags': self.tags,
                    'timestamp': timestamp,
                    'fields': fields
                }
            ]
        })
