from django.contrib.auth.forms import UserChangeForm as BaseChangeForm
from django.contrib.auth.forms import UserCreationForm as BaseCreationForm
from django.contrib.auth.forms import AdminPasswordChangeForm as BasePasswordChangeForm

from .models import Profile

__all__ = ['UserChangeForm', 'UserCreationForm', 'AdminPasswordChangeForm']


class UserChangeForm(BaseChangeForm):
    class Meta:
        model = Profile


class UserCreationForm(BaseCreationForm):
    class Meta:
        model = Profile


class AdminPasswordChangeForm(BasePasswordChangeForm):
    class Meta:
        model = Profile