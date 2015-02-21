from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class EmailBackend(ModelBackend):
    """
    Authenticates against user email.
    """

    def authenticate(self, username=None, password=None, **kwargs):
        usermodel = get_user_model()
        try:
            user = usermodel.objects.get(email=username)
            if user.check_password(password):
                return user
        except usermodel.DoesNotExist:
            return None
