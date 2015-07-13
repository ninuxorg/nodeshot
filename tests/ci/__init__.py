from nodeshot.conf.celery import init_celery


__all__ = ['app']


app = init_celery('ci')


# measure test run time with --time and --detailed:
# ./runtests.py --time
# or
# django test <module> --time --detailed

from nodeshot.core.base import tests_speedup
