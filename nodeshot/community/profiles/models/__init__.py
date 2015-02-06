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

# perform certain actions when some other parts of the application changes
# eg: update user statistics when a new device is added

from django.contrib.auth.models import Group
from django.dispatch import receiver
from django.db.models.signals import post_save


@receiver(post_save, sender=Profile)
def new_user(sender, **kwargs):
    """ operations to be performed each time a new user is created """
    created = kwargs['created']
    user = kwargs['instance']
    if created:
        # add user to default group
        # TODO: make this configurable in settings
        try:
            default_group = Group.objects.get(name='registered')
            user.groups.add(default_group)
        except Group.DoesNotExist:
            pass
        user.save()


if EMAIL_CONFIRMATION:
    from ..signals import email_confirmed

    @receiver(post_save, sender=Profile)
    def add_mail_to_user(sender, **kwargs):
        """
        Adds email to DB and sends a confirmation mail if PROFILE_EMAL_CONFIRMATION is True
        """
        user = kwargs['instance']
        # sync with EmailAddress model
        if user.email and user.email_set.filter(email=user.email).count() < 1:
            user.email_set.add_email(user, email=user.email)
            user.email_set.last().set_as_primary()

    @receiver(email_confirmed, sender=EmailConfirmation)
    def activate_user(sender, email_address, **kwargs):
        """
        activate user when primary email is confirmed
        """
        user = email_address.user
        if user.is_active is False:
            user.is_active = True
            user.save()
