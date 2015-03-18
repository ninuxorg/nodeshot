from datetime import datetime

from django.contrib.gis.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _

from jsonfield import JSONField

from nodeshot.core.base.models import BaseDate
from nodeshot.core.base.utils import ago

from . import settings as local_settings
from .utils import query, write


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

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.related_object:
            self.tags.update({
                'content_type': self.content_type.name,
                'object_id': str(self.object_id)
            })
        super(Metric, self).save(*args, **kwargs)

    def write(self, values, timestamp=None, database=None):
        """ write metric point """
        return write(name=self.name,
                     values=values,
                     tags=self.tags,
                     timestamp=timestamp,
                     database=database)

    def select(self, fields=[], since=None, limit=None):
        if fields:
            fields = ', '.join(fields)
        else:
            fields = '*'
        if not since:
            since = ago(days=30)
        if isinstance(since, datetime):
            since = since.strftime('%Y-%m-%dT%H:%M:%SZ')
        conditions = "time >= '{0}'".format(since)
        tags = ' AND '.join(["{0} = '{1}'".format(*tag) for tag in self.tags.items()])
        if tags:
            conditions = '{0} AND {1}'.format(conditions, tags)
        q = 'SELECT {fields} FROM {name} WHERE {conditions}'.format(fields=fields,
                                                                    name=self.name,
                                                                    conditions=conditions)
        if limit:
            q = '{0} LIMIT {1}'.format(q, limit)
        # return query
        return query(q)


# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
User = get_user_model()


@receiver(user_logged_in)
def user_logged_in_handler(sender, **kwargs):
    """ collect metrics about user logins """
    tags = {
        'path': kwargs['request'].path,
        'username': kwargs['user'].username,
    }
    values = {
        'value': 1,
        'path': kwargs['request'].path,
        'username': kwargs['user'].username,
        'user_id': kwargs['user'].pk
    }
    write('user_logins', values=values, tags=tags)


@receiver(post_delete, sender=User)
def user_post_delete_handler(sender, **kwargs):
    """ collect metrics about users unsubscribing """
    values = {
        'variation': -1,
        'total': User.objects.count(),
    }
    write('user_count', values=values, tags={'action': 'deleted'})


@receiver(post_save, sender=User)
def user_post_save_handler(sender, **kwargs):
    """ collect metrics about new users signing up """
    if kwargs.get('created'):
        values = {
            'variation': 1,
            'total': User.objects.count(),
        }
        write('user_count', values=values, tags={'action': 'created'})
