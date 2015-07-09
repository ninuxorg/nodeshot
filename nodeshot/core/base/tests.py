from django.conf import settings

if 'nodeshot.community.profiles' in settings.INSTALLED_APPS:
    user_fixtures = 'test_profiles.json'
else:
    user_fixtures = 'test_users.json'
