from __future__ import absolute_import
from .django import INSTALLED_APPS, MIDDLEWARE_CLASSES

# ------ SOCIAL AUTH SETTINGS ------ #

if 'social_auth' in INSTALLED_APPS:
    MIDDLEWARE_CLASSES += ('social_auth.middleware.SocialAuthExceptionMiddleware',)

    # In Django 1.6, the default session serliazer has been switched to one based on JSON,
    # rather than pickles, to improve security. Django-openid-auth does not support this
    # because it attemps to store content that is not JSON serializable in sessions.
    # See https://docs.djangoproject.com/en/dev/releases/1.6/#default-session-serialization-switched-to-json
    # for details on the Django 1.6 change.
    SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'nodeshot.community.profiles.backends.EmailBackend',
        'social_auth.backends.facebook.FacebookBackend',
        'social_auth.backends.google.GoogleOAuth2Backend',
        'nodeshot.community.profiles.social_auth_extra.github.GithubBackend',
    )

    SOCIAL_AUTH_PIPELINE = (
        'social_auth.backends.pipeline.social.social_auth_user',
        'social_auth.backends.pipeline.associate.associate_by_email',
        'social_auth.backends.pipeline.user.get_username',
        'social_auth.backends.pipeline.user.create_user',
        'social_auth.backends.pipeline.social.associate_user',
        'nodeshot.community.profiles.social_auth_extra.pipeline.load_extra_data',
        'social_auth.backends.pipeline.user.update_user_details'
    )

    SOCIAL_AUTH_ENABLED_BACKENDS = ('facebook', 'google', 'github')

    # register a new app:
    FACEBOOK_APP_ID = ''  # put your app id
    FACEBOOK_API_SECRET = ''
    FACEBOOK_EXTENDED_PERMISSIONS = ['email', 'user_about_me', 'user_birthday', 'user_hometown']

    GOOGLE_OAUTH2_CLIENT_ID = ''
    GOOGLE_OAUTH2_CLIENT_SECRET = ''

    # register a new app:
    GITHUB_APP_ID = ''
    GITHUB_API_SECRET = ''
    GITHUB_EXTENDED_PERMISSIONS = ['user:email']

    SOCIAL_AUTH_DEFAULT_USERNAME = 'new_social_auth_user'
    SOCIAL_AUTH_UUID_LENGTH = 3
    SOCIAL_AUTH_SESSION_EXPIRATION = False
    SOCIAL_AUTH_ASSOCIATE_BY_MAIL = True

    LOGIN_URL = '/'
    LOGIN_REDIRECT_URL = '/'
    LOGIN_ERROR_URL    = '/'
