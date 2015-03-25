from celery import task
from django.core import management


@task
def import_old_nodeshot(*args, **kwargs):
    """
    runs "python manage.py import_old_nodeshot"
    """
    management.call_command('import_old_nodeshot', *args, **kwargs)
