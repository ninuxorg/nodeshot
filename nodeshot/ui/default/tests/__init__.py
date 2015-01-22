from __future__ import absolute_import
from .django import DefaultUiDjangoTest  # noqa
from .selenium import DefaultUiSeleniumTest

__all__ = [
    'DefaultUiDjangoTest',
    'DefaultUiSeleniumTest'
]
