from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
User = get_user_model()

from .models import PasswordReset
from .settings import EMAIL_CONFIRMATION


__all__ = [
    'ResetPasswordForm',
    'ResetPasswordKeyForm'
]


class ResetPasswordForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"),
        required=True,
        widget=forms.TextInput(attrs={"size": "30"})
    )

    def clean_email(self):
        """ ensure email is in the database """
        if EMAIL_CONFIRMATION:
            from .models import EmailAddress
            condition = EmailAddress.objects.filter(
                email__iexact=self.cleaned_data["email"],
                verified=True
            ).count() == 0
        else:
            condition = User.objects.get(
                email__iexact=self.cleaned_data["email"],
                is_active=True
            ).count() == 0

        if condition is True:
            raise forms.ValidationError(
                _("Email address not verified for any user account")
            )
        return self.cleaned_data["email"]

    def save(self, **kwargs):
        PasswordReset.objects.create_for_user(self.cleaned_dat["email"])
        return self.cleaned_data["email"]


class ResetPasswordKeyForm(forms.Form):
    password1 = forms.CharField(
        label=_("New Password"),
        widget=forms.PasswordInput(render_value=False)
    )
    password2 = forms.CharField(
        label=_("New Password (again)"),
        widget=forms.PasswordInput(render_value=False)
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.temp_key = kwargs.pop("temp_key", None)
        super(ResetPasswordKeyForm, self).__init__(*args, **kwargs)

    def clean_password2(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(_("Password confirmation mismatch."))
        return self.cleaned_data["password2"]

    def save(self):
        # set the new user password
        user = self.user
        user.set_password(self.cleaned_data["password1"])
        user.save()
        # mark password reset object as reset
        PasswordReset.objects.filter(temp_key=self.temp_key).update(reset=True)
