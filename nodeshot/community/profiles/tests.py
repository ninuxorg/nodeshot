"""
ndoeshot.contrib.profiles tests
"""

import simplejson as json

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.nodes.models import Node
from emailconfirmation.models import EmailAddress, EmailConfirmation

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
        self.client.login(username='registered', password='tester')
    
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
    
    def test_new_profile_API(self):
        """ test new user creation through the API """
        url = reverse('api_profile_list')
        
        un_auth_client = Client()
        
        # GET 401
        response = un_auth_client.get(url)
        self.assertEqual(401, response.status_code)
        
        # GET 200
        response = self.client.get(url)
        self.assertContains(response, 'username')
        self.assertNotContains(response, 'password_confirmation')
        
        # POST 400: missing required field
        new_user = {
            "username": "new_user_test",
            "email": "new_user@testing.com",
            "password": "new_user_test"
        }
        response = self.client.post(url, json.dumps(new_user), content_type='application/json')
        self.assertContains(response, 'password_confirmation', status_code=400)
        
        # POST 400: Password confirmation mismatch
        new_user['password_confirmation'] = 'WRONG'
        response = self.client.post(url, json.dumps(new_user), content_type='application/json')
        self.assertContains(response, _('Password confirmation mismatch'), status_code=400)
        
        # POST 201: Created
        new_user['password_confirmation'] = 'new_user_test'
        response = self.client.post(url, json.dumps(new_user), content_type='application/json')
        self.assertNotContains(response, 'password_confirmation', status_code=201)
        
        user = User.objects.get(username='new_user_test')
        self.assertFalse(user.is_active)
        
        email_address = EmailAddress.objects.get(email='new_user@testing.com')
        self.assertFalse(email_address.verified)
        self.assertEqual(email_address.emailconfirmation_set.count(), 1)
        