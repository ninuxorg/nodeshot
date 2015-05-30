# part of the code of this app is based on pinax.account

from ..settings import EMAIL_CONFIRMATION


from .profile import Profile
from .social_link import SocialLink
from .password_reset import PasswordReset
from .emailconfirmation import EmailAddress, EmailConfirmation

__all__ = [
    'Profile',
    'SocialLink',
    'PasswordReset',
    'EmailAddress',
    'EmailConfirmation'
]

# ------ SIGNALS ------ #

# activate user on email confirmation

from django.dispatch import receiver

if EMAIL_CONFIRMATION:
    from ..signals import email_confirmed

    @receiver(email_confirmed, sender=EmailConfirmation)
    def activate_user(sender, email_address, **kwargs):
        """
        activate user when primary email is confirmed
        """
        user = email_address.user
        if user.is_active is False:
            user.is_active = True
            user.save()
