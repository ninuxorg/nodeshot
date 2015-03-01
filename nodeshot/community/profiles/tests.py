import simplejson as json

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.http import int_to_base36
from django.core import mail
from django.forms import ValidationError

from .settings import settings, EMAIL_CONFIRMATION

if EMAIL_CONFIRMATION:
    from .models import EmailAddress, EmailConfirmation

from .models import Profile as User
from .models import PasswordReset, SocialLink


class ProfilesTest(TestCase):
    fixtures = [
        'initial_data.json',
        'test_profiles.json',
        'test_layers.json',
        'test_status.json',
    ]

    def setUp(self):
        self.client.login(username='registered', password='tester')
        if EMAIL_CONFIRMATION:
            for user in User.objects.all():
                user.save()
            # set all email addresses as verified
            for email_address in EmailAddress.objects.all():
                email_address.verified = True
                email_address.save()
        mail.outbox = []

    def test_new_users_have_default_group(self):
        """ users should have a default group when created """
        # ensure owner of node fusolab has at least one group
        self.assertEqual(User.objects.get(username='romano').groups.count(), 1)

        # create new user and check if it has any group
        new_user = User(username='new_user_test', email='new_user@testing.com', password='tester', is_active=True)
        new_user.save()
        # retrieve again from DB just in case...
        new_user = User.objects.get(username='new_user_test')
        self.assertEqual(new_user.groups.filter(name='registered').count(), 1)

    def test_user_admin(self):
        self.client.logout()
        self.client.login(username='admin', password='tester')
        # create new user through admin
        url = reverse('admin:profiles_profile_add')
        with self.assertRaises(ValidationError):
            self.client.post(url, {
                'username': 'testing',
                'password': 'password',
                'password2': 'password'
            })

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
        self.client.logout()
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
        self.assertEqual(user.is_active, not EMAIL_CONFIRMATION)
        # ensure password is hashed
        self.assertTrue(user.has_usable_password())

        if EMAIL_CONFIRMATION:
            email_address = EmailAddress.objects.get(email='new_user@testing.com')
            self.assertTrue(email_address.primary)
            self.assertFalse(email_address.verified)
            self.assertEqual(email_address.emailconfirmation_set.count(), 1)

            key = email_address.emailconfirmation_set.all()[0].key
            confirmation_url = reverse('emailconfirmation_confirm_email', args=[key])
            response = self.client.get(confirmation_url)
            self.assertEqual(response.status_code, 302)
            self.assertIn('_auth_user_id', self.client.session)

            user = User.objects.get(username='new_user_test')
            self.assertEqual(user.is_active, True)

            # retrieve from DB again
            email_address = EmailAddress.objects.get(email='new_user@testing.com')
            self.assertTrue(email_address.verified)
            self.assertTrue(email_address.primary)

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

    def test_profile_detail_API_get_location(self):
        url = reverse('api_profile_detail', args=['registered'])
        user = User.objects.get(username='registered')

        # expects None
        user.city = ''
        user.country = ''
        user.save()
        response = self.client.get(url)
        self.assertEqual(response.data['location'], None)

        # expects City, Country
        user.city = 'Rome'
        user.country = 'Italy'
        user.save()
        response = self.client.get(url)
        self.assertEqual(response.data['location'], 'Rome, Italy')

        # expects City
        user.city = 'Rome'
        user.country = ''
        user.save()
        response = self.client.get(url)
        self.assertEqual(response.data['location'], 'Rome')

        # expects Country
        user.city = ''
        user.country = 'Italy'
        user.save()
        response = self.client.get(url)
        self.assertEqual(response.data['location'], 'Italy')

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

    def test_account_password_change_empty_API(self):
        url = reverse('api_account_password_change')
        response = self.client.post(url, {
            "current_password": "",
            "password1": "",
            "password2": ""
        }, HTTP_ACCEPT='text/html')
        self.assertContains(response, 'current_password', status_code=400)

        response = self.client.post(url, {
            "current_password": "cc",
            "password1": "cc",
            "password2": "cc"
        }, HTTP_ACCEPT='text/html')
        self.assertContains(response, 'current_password', status_code=400)

        response = self.client.post(url, {
            "current_password": "tester",
            "password1": "changed",
            "password2": "changed"
        }, HTTP_ACCEPT='text/html')
        self.assertContains(response, 'changed', status_code=200)

    def test_account_password_reset_API(self):
        url = reverse('api_account_password_reset_request_key')

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
        response = self.client.post(url, {'email': 'imnotin@the.db'})
        self.assertContains(response, 'not found', status_code=400)

        # POST 200
        user = User.objects.get(username='registered')
        response = self.client.post(url, {'email': user.email})
        self.assertEqual(200, response.status_code)
        self.assertEqual(PasswordReset.objects.filter(user=user).count(), 1, 'dummy email outbox should contain 1 email message')
        self.assertEqual(len(mail.outbox), 1, 'dummy email outbox should contain 1 email message')

        password_reset = PasswordReset.objects.get(user=user)
        uid_36 = int_to_base36(user.id)
        url = reverse('api_account_password_reset_from_key',
                      kwargs={'uidb36': uid_36, 'key': password_reset.temp_key})

        # POST 400: wrong password
        params = {'password1': 'new_password', 'password2': 'wrong'}
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
        response = self.client.post(reverse('api_account_password_reset_request_key'), {'email': user.email})
        self.assertEqual(200, response.status_code)

        # test HTML version of password reset from key
        password_reset = PasswordReset.objects.get(user=user, reset=False)
        uid = int_to_base36(password_reset.user_id)
        key = password_reset.temp_key
        url = reverse('account_password_reset_from_key', args=[uid, key])

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        response = self.client.post(url, {'password1': 'changed', 'password2': 'changed'})
        self.assertEqual(200, response.status_code)

        # ensure password has been changed
        user = User.objects.get(username='registered')
        self.assertTrue(user.check_password('changed'))

        # ensure password reset object has been used
        password_reset = PasswordReset.objects.filter(user=user).order_by('-id')[0]
        self.assertTrue(password_reset.reset)

    def test_account_password_reset_API_regression(self):
        url = reverse('api_account_password_reset_request_key')
        self.client.logout()
        user = User.objects.get(username='registered')
        response = self.client.post(url, {'email': user.email}, HTTP_ACCEPT='text/html')
        self.assertEqual(200, response.status_code)

    def test_account_login(self):
        url = reverse('api_account_login')

        # GET 403: already loggedin
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

        self.client.logout()

        # POST 400 invalid credentials
        response = self.client.post(url, {"username": "wrong", "password": "wrong"})
        self.assertContains(response, 'Ivalid login credentials', status_code=400)

        # POST 400 missing credentials
        response = self.client.post(url)
        self.assertContains(response, 'required', status_code=400)

        # POST 200 login successfull
        response = self.client.post(url, {"username": "registered", "password": "tester"})
        self.assertContains(response, 'successful')

        # GET 403: already loggedin
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

        self.client.logout()

        # POST 200 login successfull with email
        response = self.client.post(url, {"username": "registered@registered.org", "password": "tester"})
        self.assertContains(response, 'successful')

    def test_account_login_inactive(self):
        url = reverse('api_account_login')
        self.client.logout()

        # disable user
        user = User.objects.get(username='registered')
        user.is_active = False
        user.save()
        # expect 400
        response = self.client.post(url, {"username": "registered", "password": "tester"})
        self.assertContains(response, 'inactive', status_code=400)

        # re-enable user
        user.is_active = True
        user.save()
        # expect 200 login successfull
        response = self.client.post(url, {"username": "registered", "password": "tester"})
        self.assertContains(response, 'successful')

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

    def test_social_links_api(self):
        url = reverse('api_user_social_links_list', args=['romano'])

        # GET 200
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # POST 403 - only profile owner can submit new links to his profile
        response = self.client.post(url, {'url': 'http://mywebsite.com', 'description': 'mywebsite'})
        self.assertEqual(response.status_code, 403)

        # POST 201
        self.client.login(username='romano', password='tester')
        response = self.client.post(url, {'url': 'http://mywebsite.com', 'description': 'mywebsite'})
        self.assertEqual(response.status_code, 201)

        self.assertEqual(SocialLink.objects.count(), 1)

        url = reverse('api_user_social_links_detail', args=['romano', 1])

        # GET 200
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        data = json.dumps({'url': 'http://changed.com', 'description': 'changed'})

        # PUT 200
        response = self.client.put(url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, 200)

        self.client.logout()
        self.client.login(username='registered', password='tester')

        # POST 403 - only profile owner can edit
        response = self.client.put(url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, 403)

    if 'nodeshot.core.nodes' in settings.INSTALLED_APPS:
        def test_user_nodes(self):
            url = reverse('api_user_nodes', args=['romano'])

            response = self.client.get(url)
            self.assertEqual(200, response.status_code)

            response = self.client.post(url)
            self.assertEqual(405, response.status_code)

    if EMAIL_CONFIRMATION:
        def test_account_email_api(self):
            list_url = reverse('api_account_email_list')

            # GET 401 - unauthorized because not authenticated
            c = Client()
            response = c.get(list_url)
            self.assertEqual(401, response.status_code)

            # GET 200
            response = self.client.get(list_url)
            self.assertEqual(200, response.status_code)

            # POST 400 - wrong input data
            response = self.client.post(list_url)
            self.assertEqual(400, response.status_code)

            # POST 201
            user = User.objects.get(username='registered')
            email_addresses_count = EmailAddress.objects.filter(user=user).count()
            response = self.client.post(list_url, {'email': 'testing@test.com'})
            self.assertEqual(201, response.status_code)
            self.assertEqual(EmailAddress.objects.filter(user=user).count(), email_addresses_count + 1)
            # ensure is not verified nor primary
            email_address = EmailAddress.objects.filter(user=user).order_by('-id')[0]
            self.assertFalse(email_address.primary)
            self.assertFalse(email_address.verified)
            # ensure email has been sent
            self.assertEqual(len(mail.outbox), 1)
            # get email confirmation object
            email_confirmation = EmailConfirmation.objects.filter(email_address=email_address)[0]

            detail_url = reverse('api_account_email_detail', args=[email_address.pk])

            # GET detail 200
            response = self.client.get(detail_url)
            self.assertEqual(200, response.status_code)
            self.assertNotEqual(response.data['resend_confirmation'], False)

            # PUT 400 - can't make primary an unverified email address
            response = self.client.put(detail_url, data=json.dumps({'primary': True}), content_type='application/json')
            self.assertContains(response, _('Email address cannot be made primary if it is not verified first'), status_code=400)

            # POST resend confirmation
            resend_confirmation_url = reverse('api_account_email_resend_confirmation', args=[email_address.pk])
            response = self.client.post(resend_confirmation_url)
            self.assertEqual(200, response.status_code)
            # ensure email has been sent
            self.assertEqual(len(mail.outbox), 2)
            # get email confirmation object
            email_confirmation = EmailConfirmation.objects.filter(email_address=email_address).order_by('-id')[0]

            # verify email
            confirmation_url = reverse('emailconfirmation_confirm_email', args=[email_confirmation.key])
            response = self.client.get(confirmation_url)
            self.assertEqual(response.status_code, 302)

            # ensure verified and not primary (user already had a primary address)
            email_address = EmailAddress.objects.get(user=user, email='testing@test.com')
            self.assertFalse(email_address.primary)
            self.assertTrue(email_address.verified)

            # try to resend confirmation, should return error
            resend_confirmation_url = reverse('api_account_email_resend_confirmation', args=[email_address.pk])
            response = self.client.post(resend_confirmation_url)
            self.assertEqual(400, response.status_code)

            # DELETE 204 - delete the other email address
            detail_url = reverse('api_account_email_detail', args=[email_address.pk])
            response = self.client.delete(detail_url)
            self.assertEqual(response.status_code, 204)
            self.assertEqual(EmailAddress.objects.filter(user=user, email='testing@test.com').count(), 0)

            primary = email_address.user.email_set.get_primary()
            detail_url = reverse('api_account_email_detail', args=[primary.pk])
            # PUT 400 - can't unprimary
            response = self.client.put(detail_url, data=json.dumps({'primary': False}), content_type='application/json')
            self.assertContains(response, _('You must have at least one primary address.'), status_code=400)

            # DELETE 400 - can't delete because only 1 address
            response = self.client.delete(detail_url)
            self.assertEqual(response.status_code, 400)

            # add a new email address
            response = self.client.post(list_url, {'email': 'mynewemailaddress@test.com'})
            self.assertEqual(201, response.status_code)
            self.assertEqual(len(mail.outbox), 3)

            # verify new email
            email_address = EmailAddress.objects.get(user=user, email='mynewemailaddress@test.com')
            email_confirmation = EmailConfirmation.objects.filter(email_address=email_address).order_by('-id')[0]
            confirmation_url = reverse('emailconfirmation_confirm_email', args=[email_confirmation.key])
            response = self.client.get(confirmation_url)
            self.assertEqual(response.status_code, 302)

            # ensure is verified but not primary
            email_address = EmailAddress.objects.get(user=user, email='mynewemailaddress@test.com')
            self.assertFalse(email_address.primary)
            self.assertTrue(email_address.verified)

            detail_url = reverse('api_account_email_detail', args=[email_address.pk])

            # PUT 200 - make primary and ensure other one is not primary anymore
            response = self.client.put(detail_url, data=json.dumps({'primary': True}), content_type='application/json')
            self.assertEqual(response.status_code, 200)
            # ensure is primary
            email_address = EmailAddress.objects.get(user=user, email='mynewemailaddress@test.com')
            self.assertTrue(email_address.primary)
            # ensure previous one is primary
            email_address = EmailAddress.objects.get(user=user, email='registered@registered.org')
            self.assertFalse(email_address.primary)

    def test_password_confirmation_field_in_html(self):
        url = reverse('api_profile_list')
        response = self.client.get(url, HTTP_ACCEPT='text/html')

        self.assertContains(response, 'password:</label>')
        self.assertContains(response, 'password_confirmation:</label>')

    def test_delete_user(self):
        User.objects.all().delete()
        self.assertEqual(User.objects.count(), 0)

    def test_email_address_primary(self):
        user = User.objects.get(username='registered')
        self.assertEqual(user.email_set.filter(primary=True).count(), 1)

        email_address2 = EmailAddress(user=user, email='test@test.com', verified=True, primary=True)
        email_address2.full_clean()
        email_address2.save()
        self.assertEqual(user.email_set.count(), 2)
        self.assertEqual(user.email_set.filter(primary=True).count(), 1)
        self.assertEqual(user.email_set.filter(primary=True).first().email, 'test@test.com')
        self.assertEqual(User.objects.get(username='registered').email, 'test@test.com')

    def test_email_address_remove_primary(self):
        user = User.objects.get(username='registered')
        self.assertEqual(user.email_set.filter(primary=True).count(), 1)
        # setting primary as False raises validation error
        email_address = user.email_set.filter(primary=True).first()
        email_address.primary = False
        with self.assertRaises(ValidationError):
            email_address.full_clean()

    def test_add_user_creates_email(self):
        user = User(**{
            'first_name': 'test',
            'last_name': 'test',
            'username': 'test',
            'email': 'test@test.org',
            'password': 'test'
        })
        user.save()
        self.assertEqual(EmailAddress.objects.filter(email=user.email, primary=True).count(), 1)
        self.assertEqual(EmailAddress.objects.filter(email=user.email).count(), 1)
        user.delete()

        # ensure no email doesn't cause errors
        user = User(**{
            'first_name': 'test',
            'last_name': 'test',
            'username': 'test',
            'password': 'test'
        })
        user.save()
        self.assertEqual(EmailAddress.objects.filter(email=user.email).count(), 0)

    def test_set_email_to_user(self):
        # ensure no email doesn't cause errors
        user = User(**{
            'first_name': 'test',
            'last_name': 'test',
            'username': 'test',
            'password': 'test'
        })
        user.save()
        self.assertEqual(EmailAddress.objects.filter(email=user.email).count(), 0)
        # adding email later must work too
        user.email = 'test@test.org'
        user.save()
        self.assertEqual(EmailAddress.objects.filter(email=user.email, primary=True).count(), 1)
        self.assertEqual(EmailAddress.objects.filter(email=user.email).count(), 1)

        user.email = 'anotherone@another.org'
        user.save()
        self.assertEqual(user.email_set.count(), 2)
        self.assertEqual(user.email_set.get_primary().email, user.email)

    def test_user_manager_creates_email(self):
        user = User.objects.create_user(**{
            'first_name': 'test',
            'last_name': 'test',
            'username': 'test',
            'email': 'test@test.org',
            'password': 'test'
        })
        self.assertEqual(EmailAddress.objects.filter(email=user.email, primary=True).count(), 1)
        self.assertEqual(EmailAddress.objects.filter(email=user.email).count(), 1)
        user.delete()

        # ensure no email doesn't cause errors
        user = User.objects.create_user(**{
            'first_name': 'test',
            'last_name': 'test',
            'username': 'test',
            'password': 'test'
        })
        self.assertEqual(EmailAddress.objects.filter(email=user.email).count(), 0)

    def test_add_email_to_new_user(self):
        user = User(**{
            'first_name': 'test',
            'last_name': 'test',
            'username': 'test',
            'password': 'test'
        })
        user.save()
        self.assertEqual(EmailAddress.objects.filter(email=user.email).count(), 0)
        email_address = EmailAddress(user=user, email='test@test.com')
        email_address.full_clean()
        email_address.save()
        self.assertEqual(user.email_set.filter(primary=True).count(), 1)
        self.assertEqual(user.email_set.count(), 1)

    def test_skip_sync_emailaddress(self):
        user = User(**{
            'first_name': 'test',
            'last_name': 'test',
            'username': 'test',
            'email': 'test@test.org',
            'password': 'test'
        })
        user.save(sync_emailaddress=False)
        self.assertEqual(EmailAddress.objects.filter(email=user.email).count(), 0)
        user.delete()

        # ensure no email doesn't cause errors
        user = User(**{
            'first_name': 'test',
            'last_name': 'test',
            'username': 'test',
            'password': 'test'
        })
        user.save(sync_emailaddress=False)
        self.assertEqual(EmailAddress.objects.filter(email=user.email).count(), 0)

    def test_user_manager_skip_sync_emailaddress(self):
        user = User.objects.create_user(
            sync_emailaddress=False,
            **{
                'first_name': 'test',
                'last_name': 'test',
                'username': 'test',
                'email': 'test@test.org',
                'password': 'test'
            }
        )
        self.assertEqual(EmailAddress.objects.filter(email=user.email, primary=True).count(), 0)
        self.assertEqual(EmailAddress.objects.filter(email=user.email).count(), 0)
        user.delete()

        # ensure no email doesn't cause errors
        user = User.objects.create_user(
            sync_emailaddress=False,
            **{
                'first_name': 'test',
                'last_name': 'test',
                'username': 'test',
                'password': 'test'
            }
        )
        self.assertEqual(EmailAddress.objects.filter(email=user.email).count(), 0)

    def test_profile_manager_exception(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(username=None, first_name='test',
                                     last_name='test', password='test')

    def test_create_superuser(self):
        User.objects.create_superuser('newadmin', '', 'newadmin')
        user = User.objects.get(username='newadmin')
        self.assertEqual(user.email_set.count(), 0)

    if EMAIL_CONFIRMATION:
        def test_email_uniqueness(self):
            self.assertEqual(EmailAddress.objects.filter(email='admin@admin.org').count(), 1)
            user = User.objects.get(username='romano')
            email = EmailAddress(user=user, email='admin@admin.org')
            with self.assertRaises(ValidationError):
                email.full_clean()
