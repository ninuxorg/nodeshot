import requests
import json
from datetime import datetime

from django.utils.translation import ugettext_lazy as _

from social.apps.django_app.default.models import UserSocialAuth
from social.exceptions import AuthFailed

from ..settings import EMAIL_CONFIRMATION


def create_user(backend, details, response, uid, username, user=None, *args, **kwargs):
    """
    Creates user. Depends on get_username pipeline.
    """
    if user:
        return {'user': user}
    if not username:
        return None
    email = details.get('email')
    original_email = None
    # email is required
    if not email:
        message = _("""your social account needs to have a verified email address in order to proceed.""")
        raise AuthFailed(backend, message)
    # Avoid hitting field max length
    if email and len(email) > 75:
        original_email = email
        email = ''
    return {
        'user': UserSocialAuth.create_user(username=username,
                                           email=email,
                                           sync_emailaddress=False),
        'original_email': original_email,
        'is_new': True
    }


def load_extra_data(backend, details, response, uid, user, social_user=None, *args, **kwargs):
    """
    Load extra data from provider and store it on current UserSocialAuth extra_data field.
    """
    social_user = social_user or UserSocialAuth.get_social_auth(backend.name, uid)
    # create verified email address
    if kwargs['is_new'] and EMAIL_CONFIRMATION:
        from ..models import EmailAddress
        # check if email exist before creating it
        # we might be associating an exisiting user
        if EmailAddress.objects.filter(email=user.email).count() < 1:
            EmailAddress.objects.create(user=user,
                                        email=user.email,
                                        verified=True,
                                        primary=True)

    if social_user:
        extra_data = backend.extra_data(user, uid, response, details)
        if kwargs.get('original_email') and 'email' not in extra_data:
            extra_data['email'] = kwargs.get('original_email')
        # update extra data if anything has changed
        if extra_data and social_user.extra_data != extra_data:
            if social_user.extra_data:
                social_user.extra_data.update(extra_data)
            else:
                social_user.extra_data = extra_data
            social_user.save()
        # fetch additional data from facebook on creation
        if backend.name == 'facebook' and kwargs['is_new']:
            response = json.loads(requests.get('https://graph.facebook.com/%s?access_token=%s' % (extra_data['id'], extra_data['access_token'])).content)
            try:
                user.city, user.country = response.get('hometown').get('name').split(', ')
            except (AttributeError, TypeError):
                pass
            try:
                user.birth_date = datetime.strptime(response.get('birthday'), '%m/%d/%Y').date()
            except (AttributeError, TypeError):
                pass
            user.save()
        return {'social_user': social_user}
