from django.apps import AppConfig as BaseConfig


class AppConfig(BaseConfig):
    name = 'nodeshot.core.cms'

    def ready(self):
        from . import signals  # noqa
