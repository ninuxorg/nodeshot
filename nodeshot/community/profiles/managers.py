from django.utils import timezone
from django.contrib.auth.models import UserManager


class ProfileManager(UserManager):
    """
    adds support for sync_emailaddress parameter
    """
    def _create_user(self, username, email, password, is_staff,
                     is_superuser, sync_emailaddress=True, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db, sync_emailaddress=sync_emailaddress)
        return user

    def create_user(self, username, email=None, password=None,
                    sync_emailaddress=True, **extra_fields):
        return self._create_user(username, email, password, False, False,
                                 sync_emailaddress, **extra_fields)
