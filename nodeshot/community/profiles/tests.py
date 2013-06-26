"""
ndoeshot.contrib.profiles tests
"""

import simplejson as json

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

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
        self.PROFILE_EMAIL_CONFIRMATION = settings.NODESHOT['SETTINGS'].get('PROFILE_EMAIL_CONFIRMATION', True)
    
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
    
    def test_profile_list_API(self):
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
        self.assertEqual(user.is_active, not self.PROFILE_EMAIL_CONFIRMATION)
        
        if self.PROFILE_EMAIL_CONFIRMATION:
            email_address = EmailAddress.objects.get(email='new_user@testing.com')
            self.assertFalse(email_address.verified)
            self.assertEqual(email_address.emailconfirmation_set.count(), 1)
            
            key = email_address.emailconfirmation_set.all()[0].key
            confirmation_url = reverse('confirm_email', args=[key])
            response = self.client.get(confirmation_url)
            self.assertEqual(response.status_code, 200)
            
            user = User.objects.get(username='new_user_test')
            self.assertEqual(user.is_active, True)
    
    def test_profile_detail_API(self):
        """ test new user creation through the API """
        url = reverse('api_profile_detail', args=['registered'])
        
        # GET 200
        response = self.client.get(url)
        self.assertContains(response, 'username')
        self.assertNotContains(response, 'password')
        self.assertNotContains(response, 'email')
        
        # PUT 200
        profile = {
            "first_name": "Registered",
            "last_name": "User",
            "about": "Lorem ipsum dolor...",
            "gender": "M",
            "birth_date": "1987-03-23",
            "address": "Via Prova 1",
            "city": "Rome",
            "country": "Italy"
        }
        response = self.client.put(url, json.dumps(profile), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username='registered')
        self.assertEqual(user.first_name, 'Registered')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.about, 'Lorem ipsum dolor...')
        self.assertEqual(user.gender, 'M')
        self.assertEqual(user.birth_date.strftime('%Y-%m-%d'), '1987-03-23')
        self.assertEqual(user.address, 'Via Prova 1')
        self.assertEqual(user.city, 'Rome')
        self.assertEqual(user.country, 'Italy')
        
        # PUT 403
        # try modifying another user's profile
        url = reverse('api_profile_detail', args=['romano'])
        response = self.client.put(url, json.dumps(profile), content_type='application/json')
        self.assertEqual(response.status_code, 403)
    
    def test_account_detail_API(self):
        url = reverse('api_account_detail')
        
        un_auth_client = Client()
        
        # GET 401
        response = un_auth_client.get(url)
        self.assertEqual(401, response.status_code)
        
        # GET 200
        response = self.client.get(url)
        self.assertContains(response, 'profile')
        self.assertContains(response, 'change_password')
    
    def test_account_password_change_API(self):
        url = reverse('api_account_password_change')
        
        un_auth_client = Client()
        
        # GET 401
        response = un_auth_client.get(url)
        self.assertEqual(401, response.status_code)
        
        # GET 405
        response = self.client.get(url)
        self.assertEqual(405, response.status_code)
        
        # POST 400: wrong current password
        new_password = {}
        response = self.client.post(url, new_password)
        self.assertContains(response, 'current_password', status_code=400)
        self.assertContains(response, 'password', status_code=400)
        self.assertContains(response, 'password_confirmation', status_code=400)
        
        # POST 400: wrong current password
        new_password = {
            "current_password": "wrong",
            "password": "new_password",
            "password_confirmation": "new_password"
        }
        response = self.client.post(url, new_password)
        self.assertContains(response, 'Current password', status_code=400)
        
        # POST 400: password mismatch
        new_password = {
            "current_password": "tester",
            "password": "new_password",
            "password_confirmation": "wrong"
        }
        response = self.client.post(url, new_password)
        self.assertContains(response, 'mismatch', status_code=400)
        
        # POST 200: password changed
        new_password = {
            "current_password": "tester",
            "password": "new_password",
            "password_confirmation": "new_password"
        }
        response = self.client.post(url, new_password)
        self.assertContains(response, 'successfully')
        
        # ensure password has really changed
        user = User.objects.get(username='registered')
        self.assertEqual(user.check_password('new_password'), True)
        
        self.client.logout()
        self.client.login(username='registered', password='new_password')
        
        # GET 405 again
        response = self.client.get(url)
        self.assertEqual(405, response.status_code)