from django.apps import AppConfig as BaseConfig


class AppConfig(BaseConfig):
    name = 'nodeshot.ui.default'
    label = 'nodeshot default ui'
    verbose_name = "Nodeshot default UI"
