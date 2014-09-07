import requests
import simplejson as json
from datetime import datetime

from social_auth.models import UserSocialAuth

from ..settings import EMAIL_CONFIRMATION


def load_extra_data(backend, details, response, uid, user, social_user=None,
                    *args, **kwargs):
    """Load extra data from provider and store it on current UserSocialAuth
    extra_data field.
    """
    social_user = social_user or \
                  UserSocialAuth.get_social_auth(backend.name, uid)

    if kwargs['is_new'] and EMAIL_CONFIRMATION:
        from ..models import EmailAddress
        emailaddress = EmailAddress(**{
            'user': user,
            'email': user.email,
            'verified': True,
            'primary': True
        })
        emailaddress.save()

    if social_user:
        extra_data = backend.extra_data(user, uid, response, details)
        if kwargs.get('original_email') and 'email' not in extra_data:
            extra_data['email'] = kwargs.get('original_email')
        if extra_data and social_user.extra_data != extra_data:
            if social_user.extra_data:
                social_user.extra_data.update(extra_data)
            else:
                social_user.extra_data = extra_data
            social_user.save()

        if backend.name == 'facebook' and kwargs['is_new']:
            response = json.loads(requests.get('https://graph.facebook.com/%s?access_token=%s' % (extra_data['id'], extra_data['access_token'])).content)

            try:
                user.city, user.country = response.get('hometown').get('name').split(', ')
            except AttributeError:
                pass

            try:
                user.birth_date = datetime.strptime(response.get('birthday'), '%m/%d/%Y').date()
            except AttributeError:
                pass

            user.save()

        return {'social_user': social_user}
