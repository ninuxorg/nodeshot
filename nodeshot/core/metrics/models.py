from datetime import datetime

from django.contrib.gis.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _

from jsonfield import JSONField

from nodeshot.core.base.models import BaseDate

from .utils import query, write


class Metric(BaseDate):
    name = models.CharField(_('name'), max_length=75)
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    related_object = generic.GenericForeignKey('content_type', 'object_id')
    tags = JSONField(_('tags'), blank=True, default={})
    query = models.CharField(_('query'), blank=True, max_length=255, help_text='default query')

    class Meta:
        unique_together = ('name', 'tags', 'content_type', 'object_id')

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.related_object:
            self.tags.update({
                'content_type': self.content_type.name,
                'object_id': str(self.object_id)
            })
        if not self.query:
            self.query = self.select(sql_only=True)
        super(Metric, self).save(*args, **kwargs)

    def write(self, values, timestamp=None, database=None):
        """ write metric point """
        return write(name=self.name,
                     values=values,
                     tags=self.tags,
                     timestamp=timestamp,
                     database=database)

    def select(self, fields=[], since=None, limit=None, q=None, sql_only=False):
        if q is not None and ('DROP' in q or 'DELETE' in q):
            q = None
        if not q:
            if fields:
                fields = ', '.join(fields)
            else:
                fields = '*'
            if not since:
                since = 'now() - 30d'
            if isinstance(since, datetime):
                since = "'{0}'".format(since.strftime('%Y-%m-%dT%H:%M:%SZ'))
            conditions = "time >= {0}".format(since)
            tags = ' AND '.join(["{0} = '{1}'".format(*tag) for tag in self.tags.items()])
            if tags:
                conditions = '{0} AND {1}'.format(conditions, tags)
            q = 'SELECT {fields} FROM {name} WHERE {conditions}'.format(fields=fields,
                                                                        name=self.name,
                                                                        conditions=conditions)
            if limit:
                q = '{0} LIMIT {1}'.format(q, limit)
        if sql_only:
            return q
        # return query
        return query(q)


# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
User = get_user_model()


@receiver(user_logged_in, dispatch_uid='user_loggedin')
def user_loggedin(sender, **kwargs):
    """ collect metrics about user logins """
    tags = {
        'user_id': str(kwargs['user'].pk),
        'username': kwargs['user'].username,
    }
    values = {
        'value': 1,
        'path': kwargs['request'].path
    }
    write('user_logins', values=values, tags=tags)


@receiver(post_delete, sender=User, dispatch_uid='user_created')
def user_created(sender, **kwargs):
    """ collect metrics about users unsubscribing """
    write('user_variations', {'variation': -1}, tags={'action': 'deleted'})
    write('user_count', {'total': User.objects.count()})


@receiver(post_save, sender=User, dispatch_uid='user_deleted')
def user_deleted(sender, **kwargs):
    """ collect metrics about new users signing up """
    if kwargs.get('created'):
        write('user_variations', {'variation': 1}, tags={'action': 'created'})
        write('user_count', {'total': User.objects.count()})
