from django.db.models.signals import post_syncdb
from django.contrib.auth import models

from .utils import create_database


def create_database_signal(sender, **kwargs):
    create_database()


post_syncdb.connect(create_database_signal, sender=models)
