"""
nodeshot.community.mailing unit tests
"""

import datetime

from django.test import TestCase
from django.utils.translation import ugettext as _
from django.core import mail
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.timezone import utc
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
User = get_user_model()

from nodeshot.core.layers.models import Layer
from nodeshot.core.nodes.models import Node
from nodeshot.core.base.tests import user_fixtures
from nodeshot.community.profiles.settings import EMAIL_CONFIRMATION

from .models import Inward, Outward
from .models.choices import FILTERS

if EMAIL_CONFIRMATION:
    from nodeshot.community.profiles.models import EmailAddress


class MailingTest(TestCase):
    fixtures = [
        'initial_data.json',
        user_fixtures,
        'test_layers.json',
        'test_status.json',
        'test_nodes.json'
    ]

    def setUp(self):
        # create outward record
        self.message = Outward.objects.create(
            status=0,
            subject='test message',
            message='This is a test message, be sure this text is longer than the minimum required',
            is_scheduled=False,
            is_filtered=False
        )
        self.msg = Outward(
            status=0,
            subject='This is a test',
            message=self.message.message,
        )
        mail.outbox = []
        if EMAIL_CONFIRMATION:
            # set all email addresses as verified
            for email_address in EmailAddress.objects.all():
                email_address.verified = True
                email_address.save()

    def test_inward_model(self):
        """ ensure inward model validation works as expected """
        message = Inward(message='this is a test to ensure inward model validation works as expected')
        content_type = ContentType.objects.only('id', 'model').get(model='node')
        message.content_type = content_type
        message.object_id = 1
        user = User.objects.get(pk=1)
        # ensure validation error
        try:
            message.full_clean()
            self.fail('ValidationError not raised')
        except ValidationError as e:
            self.assertIn(_('If sender is not specified from_name and from_email must be filled in'), e.message_dict['__all__'][0])
        # ensure validation error
        try:
            message.from_email = user.email
            message.from_name = user.get_full_name()
            message.full_clean()
            self.fail('ValidationError not raised')
        except ValidationError as e:
            self.assertIn(_('This field cannot be blank'), e.message_dict['user'][0])
        # ensure no validation error
        message.full_clean(exclude=['user'])
        # empty from_name and from_email, we need to ensure they'll filled automatically
        message.from_name = None
        message.from_email = None
        # set user
        message.user = user
        message.full_clean()
        message.save()
        # expect correct mail sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(message.status, 1)
        self.assertEqual(message.from_name, user.get_full_name())
        self.assertEqual(message.from_email, user.email)

    def test_contact_node_api(self):
        """ ensure contact node api works as expected """
        url = reverse('api_node_contact', args=['fusolab'])
        self.client.login(username='admin', password='tester')
        mail.outbox = []

        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

        response = self.client.post(url, {'message': 'ensure contact node api works as expected'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(Inward.objects.count(), 1)

    def test_contact_user_api(self):
        """ ensure contact user api works as expected """
        url = reverse('api_user_contact', args=['romano'])
        self.client.login(username='admin', password='tester')
        mail.outbox = []

        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

        response = self.client.post(url, {'message': 'ensure contact user api works as expected'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(Inward.objects.count(), 1)

    def test_contact_layer_api(self):
        """ ensure contact layer api works as expected """
        url = reverse('api_layer_contact', args=['rome'])
        self.client.login(username='admin', password='tester')
        mail.outbox = []

        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

        response = self.client.post(url, {'message': 'ensure contact user api works as expected'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(Inward.objects.count(), 1)

        vienna = Layer.objects.get(slug='vienna')
        vienna.email = ''
        vienna.save()

        # cannot be contacted because no email nor mantainers specified
        url = reverse('api_layer_contact', args=['vienna'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)

        response = self.client.post(url, {'message': 'ensure contact user api works as expected'})
        self.assertEqual(response.status_code, 400)

    def test_contact_api_validation_error(self):
        url = reverse('api_layer_contact', args=['rome'])
        self.client.login(username='admin', password='tester')
        mail.outbox = []

        response = self.client.post(url, {'message': 'short'})
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(Inward.objects.count(), 0)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Ensure this value has at least', response.data['message'][0])

    def test_no_filter(self):
        """ *** Test no filtering, send to all *** """
        # count users
        users = User.objects.filter(is_active=True)
        recipients = self.message.get_recipients()

        # simplest case: send to all
        # fail if recipient list length and user list length differ
        self.assertEqual(len(recipients), len(users))
        # fail if user emails are not in recipients
        for user in users:
            self.assertTrue(user.email in recipients)

    def test_outward_admin_send_action(self):
        """ simulate sending mails from the admin """
        from django.http.request import HttpRequest
        from django.contrib.admin.sites import AdminSite
        from .admin import OutwardAdmin
        admin = OutwardAdmin(Outward, AdminSite())
        request = HttpRequest()
        self.assertEqual(Outward.objects.count(), 1)
        # trigger send action
        admin.send(request, Outward.objects.all())
        # ensure outward message has status == sent
        message = Outward.objects.first()
        self.assertEqual(message.status, 2)
        # ensure messages have been sent to users
        self.assertEqual(len(mail.outbox), User.objects.count())

    def test_group_filtering(self):
        """ *** Test group filtering in multiple combinations *** """
        combinations = [
            '1', '2', '3', '0',
            '1,2', '1,3', '1,0', '2,3', '2,0', '3,0',
            '1,2,3', '1,2,0', '1,3,0', '2,3,0',
            '1,2,3,0'
        ]
        # prepare record
        message = self.message
        message.is_filtered = True
        message.filters = '1'

        for combo in combinations:
            # test multiple groups
            groups = combo.split(',')
            # init empty Q
            q = Q()
            for group in groups:
                # if not superuser case
                if group != '0':
                    # add another group to the Q
                    q = q | Q(groups=group)
                # superuser case
                else:
                    # group 0 wouldn't be correct, therefore we use is_superuser=True
                    q = q | Q(is_superuser=True)
            # and is_active = True
            q = q & Q(is_active=True)
            # retrieve users
            users = User.objects.filter(q)
            message.groups = combo
            recipients = message.get_recipients()
            # fail if recipient list length and user list length differ
            self.assertEqual(len(recipients), len(users))
            # fail if user emails are not in recipients
            for user in users:
                self.assertTrue(user.email in recipients)

    def test_layer_filtering(self):
        """ *** Test layer filtering in multiple combinations *** """
        combinations = [
            '1', '2', '3',
            '1,2', '1,3', '2,3',
            '1,2,3'
        ]
        # prepare record
        message = self.message
        message.is_filtered = True
        message.filters = '2'

        for combo in combinations:
            layers = combo.split(',')
            # init empty Q
            q = Q()
            for layer in layers:
                q = q | Q(layer=layer)
            # retrieve nodes
            nodes = Node.objects.filter(q)
            # layers id list
            message.layers = [int(layer) for layer in layers]
            # retrieve recipients according to model code
            recipients = message.get_recipients()
            # retrieve list of emails
            emails = []
            for node in nodes:
                if node.user.email not in emails:
                    emails += [node.user.email]
            # fail if recipient list length and user list length differ
            self.assertEqual(len(recipients), len(emails))
            # fail if user emails are not in recipients
            for email in emails:
                self.assertTrue(email in recipients)

    def test_user_filtering(self):
        """ *** Test recipient filtering by user *** """
        combinations = [
            '1', '2', '3', '4', '5', '6', '7', '8',
            '1,2', '2,3', '3,4', '5,6'
            '1,2,3', '3,4,5', '6,7,8'
            '1,2,3,4', '5,6,7,8',
            '1,2,3,4,5,6,7,8'
        ]
        # prepare record
        message = self.message
        message.is_filtered = True
        message.filters = '3'

        for combo in combinations:
            # users id list
            users_string = combo.split(',')
            user_ids = [int(user) for user in users_string]
            # selected users
            message.users = user_ids
            # retrieve recipients according to the model code
            recipients = message.get_recipients()
            # init empty Q
            q = Q()
            # retrieve users
            for user in user_ids:
                q = q | Q(id=user)
            # only active users
            q = q & Q(is_active=True)
            users = User.objects.filter(q)
            # fail if recipient list length and user list length differ
            self.assertEqual(len(recipients), len(users))
            # fail if user emails are not in recipients
            for user in users:
                self.assertTrue(user.email in recipients)

    def test_group_and_layer_filtering(self):
        """ *** Test group & layer filtering in multiple combinations *** """
        combinations = [
            {'groups': '1', 'layers': '1'},
            {'groups': '2', 'layers': '2'},
            {'groups': '1,2', 'layers': '1'},
            {'groups': '1,2,3', 'layers': '1,2'},
            {'groups': '1,2', 'layers': '1,2,3'},
            {'groups': '3', 'layers': '1,2,3'}
        ]
        # prepare record
        message = self.message
        message.is_filtered = True
        message.filters = '1,2'

        for combo in combinations:
            groups = combo['groups'].split(',')
            layers = combo['layers'].split(',')

            # GROUPS
            q1 = Q()
            for group in groups:
                # if not superuser case
                if group != '0':
                    # add another group to the Q
                    q1 = q1 | Q(user__groups=group)
                # superuser case
                else:
                    # group 0 wouldn't be correct, therefore we use is_superuser=True
                    q1 = q1 | Q(user__is_superuser=True)
            # and is_active = True
            q1 = q1 & Q(user__is_active=True)

            # LAYERS
            q2 = Q()
            for layer in layers:
                q2 = q2 | Q(layer=layer)
            # retrieve nodes
            nodes = Node.objects.filter(q1 & q2).select_related()

            # message group & layers
            message.groups = combo['groups']
            message.layers = [int(layer) for layer in layers]

            # retrieve recipients according to model code
            recipients = message.get_recipients()
            # retrieve list of emails
            emails = []
            for node in nodes:
                if node.user.email not in emails:
                    emails += [node.user.email]
            # fail if recipient list length and user list length differ
            self.assertEqual(len(recipients), len(emails))
            # fail if user emails are not in recipients
            for email in emails:
                self.assertTrue(email in recipients)

    def test_user_and_layer_filtering(self):
        """ *** Test recipient filtering by user & layers *** """
        combinations = [
            {'users': '1', 'layers': '1'},
            {'users': '2', 'layers': '2'},
            {'users': '1,2', 'layers': '1'},
            {'users': '1,2,3', 'layers': '1,2'},
            {'users': '1,2', 'layers': '1,2,3'},
            {'users': '3', 'layers': '1,2,3'},
            {'users': '3,4,5,6,7', 'layers': '1'}
        ]
        # prepare record
        message = self.message
        message.is_filtered = True
        message.filters = '2,3'

        for combo in combinations:
            users = combo['users'].split(',')
            layers = combo['layers'].split(',')

            # ZONES
            q1 = Q()
            for layer in layers:
                q1 = q1 | Q(layer=layer)
            # retrieve nodes
            nodes = Node.objects.filter(q1).select_related()

            # prepare Q object for user query
            q2 = Q()
            for user in users:
                q2 = q2 | Q(pk=user)
            q2 = q2 & Q(is_active=True)

            # message users & layers
            message.users = [int(user) for user in users]
            message.layers = [int(layer) for layer in layers]

            # retrieve chosen users
            users = User.objects.filter(q2)

            # retrieve recipients according to model code
            recipients = message.get_recipients()

            # retrieve list of emails
            emails = []
            for node in nodes:
                if node.user.email not in emails:
                    emails.append(node.user.email)

            # add emails of selected users if necessary
            for user in users:
                if user.email not in emails:
                    emails.append(user.email)

            # fail if recipient list length and user list length differ
            self.assertEqual(len(recipients), len(emails))
            # fail if user emails are not in recipients
            for email in emails:
                self.assertTrue(email in recipients)

    # TODO:
    # test html/plain-text format

    def test_outward_validation_scheduled1(self):
        """ *** A scheduled message without any value for scheduled date and time should not pass validation *** """
        self.msg.is_scheduled = 1
        self.msg.scheduled_date = None
        self.msg.scheduled_time = None
        self.assertRaises(ValidationError, self.msg.full_clean)

    def test_outward_validation_scheduled2(self):
        """ *** A scheduled message without any value for scheduled time should not pass validation *** """
        self.msg.is_scheduled = 1
        self.msg.scheduled_time = None
        self.msg.scheduled_date = datetime.datetime.utcnow().replace(tzinfo=utc).date() + datetime.timedelta(days=1)
        self.assertRaises(ValidationError, self.msg.full_clean)

    def test_outward_validation_scheduled3(self):
        """ *** A scheduled message without any value for scheduled date should not pass validation *** """
        self.msg.is_scheduled = 1
        self.msg.scheduled_date = None
        self.msg.scheduled_time = '00'
        self.assertRaises(ValidationError, self.msg.full_clean)

    def test_outward_validation_scheduled4(self):
        """ *** A scheduled message with both date and time should pass validation *** """
        self.msg.is_scheduled = 1
        self.msg.scheduled_date = datetime.datetime.utcnow().replace(tzinfo=utc).date() + datetime.timedelta(days=1)
        self.msg.scheduled_time = '00'
        self.msg.full_clean()

    def test_outward_validate_scheduled5(self):
        """ *** A new message with a past scheduled date should not pass validation *** """
        self.msg.is_scheduled = 1
        self.msg.scheduled_date = datetime.datetime.utcnow().replace(tzinfo=utc).date() - datetime.timedelta(days=1)
        self.msg.scheduled_time = '00'
        self.assertRaises(ValidationError, self.msg.full_clean)

    def test_outward_validate_filters1(self):
        """ *** A new message with is_filtered == True and no selected filter should not pass validation *** """
        self.msg.is_scheduled = 0
        self.msg.scheduled_date = None
        self.msg.scheduled_time = None
        self.msg.is_filtered = 1
        self.assertRaises(ValidationError, self.msg.full_clean)

    def test_outward_validate_filters2(self):
        """ *** A new message with group filtering active but not selected group should not pass validation *** """
        self.msg.is_scheduled = 0
        self.msg.is_filtered = 1
        self.msg.filters = '%s' % FILTERS.get('groups')
        self.msg.groups = ''
        self.assertRaises(ValidationError, self.msg.full_clean)

    # the following two validation routine require more cumbersome procedures ... can't be bothered right now!

    # def test_outward_validate_filters3(self):
    #    """ *** A new message with user filtering active but not selected group should not pass validation *** """
    #    self.msg.is_scheduled = 0
    #    self.msg.is_filtered = 1
    #    self.msg.filters = '%s' % FILTERS.get('users')
    #    self.msg.users = []
    #    self.assertRaises(ValidationError, self.msg.full_clean)
    #
    # def test_outward_validate_filters4(self):
    #    """ *** A new message with layer filtering active but not selected group should not pass validation *** """
    #    self.msg.is_scheduled = 0
    #    self.msg.is_filtered = 1
    #    self.msg.filters = '%s' % FILTERS.get('layers')
    #    self.msg.layers = []
    #    self.assertRaises(ValidationError, self.msg.full_clean)
    #
    # def test_outward_plaintext(self):
    #    """ *** TODO: write a test that verifies email is correctly sent as plain text *** """
    #    self.assertEqual(False, True)
    #
    # def test_outward_html(self):
    #    """ *** TODO: write a test that verifies email is correctly sent both as plain text and HTML *** """
    #    self.assertEqual(False, True)
