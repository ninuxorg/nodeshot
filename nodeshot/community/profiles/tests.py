"""
ndoeshot.contrib.profiles tests
"""

from django.test import TestCase

from nodeshot.core.nodes.models import Node
#from nodeshot.core.nodes.models.choices import NODE_STATUS

from .models import Profile as User


class ProfilesTest(TestCase):
    
    fixtures = [
        'initial_data.json',
        'test_profiles.json',
        'test_layers.json',
        'test_nodes.json',
    ]
    
    def setUp(self):
        self.fusolab = Node.objects.get(slug='fusolab')
    
    def test_new_users_have_default_group(self):
        """ users should have a default group when created """
        # ensure owner of node fusolab has at least one group
        self.assertEqual(self.fusolab.user.groups.count(), 1)
        
        # create new user and check if it has any group
        new_user = User(username='new_user_test', email='new_user@testing.com', password='tester')
        new_user.save()
        # retrieve again from DB just in case...
        new_user = User.objects.get(username='new_user_test')
        self.assertEqual(new_user.groups.filter(name='registered').count(), 1)