"""
ndoeshot.contrib.profiles tests
"""

import simplejson as json

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.http import int_to_base36
from django.core import mail
from django.conf import settings

from nodeshot.core.nodes.models import Node
from emailconfirmation.models import EmailAddress, EmailConfirmation

from .models import Profile as User
from .models import PasswordReset


class ProfilesTest(TestCase):
    
    fixtures = [
        'initial_data.json',
        'test_profiles.json',
        'test_layers.json',
        'test_status.json',
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
        
        self.client.logout()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
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
        self.assertContains(response, 'password1', status_code=400)
        self.assertContains(response, 'password2', status_code=400)
        
        # POST 400: wrong current password
        new_password = {
            "current_password": "wrong",
            "password1": "new_password",
            "password2": "new_password"
        }
        response = self.client.post(url, new_password)
        self.assertContains(response, 'Current password', status_code=400)
        
        # POST 400: password mismatch
        new_password = {
            "current_password": "tester",
            "password1": "new_password",
            "password2": "wrong"
        }
        response = self.client.post(url, new_password)
        self.assertContains(response, 'mismatch', status_code=400)
        
        # POST 200: password changed
        new_password = {
            "current_password": "tester",
            "password1": "new_password",
            "password2": "new_password"
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
    
    def test_account_password_reset_API(self):
        url = reverse('api_account_password_reset')
        
        # GET 403 - user must not be authenticated
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
        
        self.client.logout()
        
        # GET 405
        response = self.client.get(url)
        self.assertEqual(405, response.status_code)
        
        # POST 400: missing required field
        response = self.client.post(url)
        self.assertContains(response, 'required', status_code=400)
        
        # POST 400: email not found in the DB
        response = self.client.post(url, { 'email': 'imnotin@the.db' })
        self.assertContains(response, 'address not verified for any', status_code=400)
        
        # POST 200
        user = User.objects.get(username='registered')
        
        if self.PROFILE_EMAIL_CONFIRMATION:
            email_address = EmailAddress(user=user, email=user.email, verified=True, primary=True)
            email_address.save()
        
        response = self.client.post(url, { 'email': user.email })
        self.assertEqual(200, response.status_code)
        
        self.assertEqual(PasswordReset.objects.filter(user=user).count(), 1, 'dummy email outbox should contain 1 email message')
        self.assertEqual(len(mail.outbox), 1, 'dummy email outbox should contain 1 email message')
        
        password_reset = PasswordReset.objects.get(user=user)
        
        uid_36 = int_to_base36(user.id)
        url = reverse('api_account_password_reset_key',
                      kwargs={ 'uidb36': uid_36, 'key': password_reset.temp_key })
        
        # POST 400: wrong password
        params = { 'password1': 'new_password', 'password2': 'wrong' }
        response = self.client.post(url, params)
        self.assertContains(response, '"password2"', status_code=400)
        
        # correct
        params['password2'] = 'new_password'
        response = self.client.post(url, json.dumps(params), content_type='application/json')
        self.assertContains(response, '"detail"')
        
        # ensure password has been changed
        user = User.objects.get(username='registered')
        self.assertTrue(user.check_password('new_password'))
        
        # ensure password reset object has been used
        password_reset = PasswordReset.objects.get(user=user)
        self.assertTrue(password_reset.reset)
        
        # request a new password reset key
        response = self.client.post(reverse('api_account_password_reset'), { 'email': user.email })
        self.assertEqual(200, response.status_code)
        
        # test HTML version of password reset from key
        password_reset = PasswordReset.objects.get(user=user, reset=False)
        uid = int_to_base36(password_reset.user_id)
        key = password_reset.temp_key
        url = reverse('account_password_reset_key', args=[uid, key])
        
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
        response = self.client.post(url, { 'password1': 'changed', 'password2': 'changed' } )
        self.assertEqual(200, response.status_code)
        
        # ensure password has been changed
        user = User.objects.get(username='registered')
        self.assertTrue(user.check_password('changed'))
        
        # ensure password reset object has been used
        password_reset = PasswordReset.objects.filter(user=user).order_by('-id')[0]
        self.assertTrue(password_reset.reset)
    
    def test_account_login(self):
        url = reverse('api_account_login')
        
        # GET 403: already loggedin
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
        
        self.client.logout()
        
        # POST 400 bad credentials
        response = self.client.post(url, { "username": "wrong", "password": "wrong" })
        self.assertContains(response, 'not correct', status_code=400)
        
        # POST 400 missing credentials
        response = self.client.post(url)
        self.assertContains(response, 'required', status_code=400)
        
        # POST 200 login successfull
        response = self.client.post(url, { "username": "registered", "password": "tester" })
        self.assertContains(response, 'successful')
        
        # GET 403: already loggedin
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
    
    def test_account_logout(self):
        url = reverse('api_account_logout')
        account_url = reverse('api_account_detail')
        
        # GET 405
        response = self.client.get(url)
        self.assertEqual(405, response.status_code)
        
        # Ensure is authenticated
        response = self.client.get(account_url)
        self.assertEqual(200, response.status_code)
        
        # POST 200
        response = self.client.post(url)
        self.assertEqual(200, response.status_code)
        
        # Ensure is NOT authenticated
        response = self.client.get(account_url)
        self.assertEqual(401, response.status_code)
    
    if 'nodeshot.core.nodes' in settings.INSTALLED_APPS:
        def test_user_nodes(self):
            url = reverse('api_user_nodes', args=['romano'])
            
            response = self.client.get(url)
            self.assertEqual(200, response.status_code)
            
            response = self.client.post(url)
            self.assertEqual(405, response.status_code)
        