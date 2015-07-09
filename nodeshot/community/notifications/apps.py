from django.apps import AppConfig as BaseConfig


class AppConfig(BaseConfig):
    name = 'nodeshot.community.notifications'

    def ready(self):
        from . import signals
