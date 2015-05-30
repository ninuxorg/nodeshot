from nodeshot.conf.celery import init_celery


__all__ = ['app']


app = init_celery('{{ project_name }}')
