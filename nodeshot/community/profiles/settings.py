from django.conf import settings


EMAIL_CONFIRMATION = getattr(settings, 'PROFILE_EMAIL_CONFIRMATION', True)
REQUIRED_FIELDS = getattr(settings, 'PROFILE_REQUIRED_FIELDS', ['email'])
