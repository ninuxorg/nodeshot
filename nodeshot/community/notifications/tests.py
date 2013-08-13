from django.test.client import Client
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.core import mail
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()

from nodeshot.core.base.tests import user_fixtures, BaseTestCase

#from models import Notification, NOTIFICATION_TYPES, NOTIFICATION_DESCRIPTIONS

from .models import *


class TestNotification(BaseTestCase):
    """
    Test Notifications
    """
    
    fixtures = [
        'initial_data.json',
        user_fixtures,
        'test_layers.json',
        'test_status.json',
    ]
    
    def test_notification_to_herself(self):
        """ An user cannot send a notification to herself/himself """
        n = Notification(
            to_user_id=1,
            from_user_id=1,
            type='new_node_created',
            text=settings.NODESHOT['NOTIFICATIONS'].get('new_node_created') % 'test_node'
        )
        self.assertRaises(ValidationError, n.full_clean)
    
    #def test_email_is_sent(self):
    #    """ Test user notification are correctly sent via email """
    #    n = Notification(
    #        to_user_id=1,
    #        from_user_id=2,
    #        type=NOTIFICATION_TYPES['friend_request_received'],
    #        description=NOTIFICATION_DESCRIPTIONS['friend_request_received'] % 'user1'
    #    )
    #    self.assertTrue(n.send_email())
    #    self.assertEqual(len(mail.outbox), 1)
    #
    #def test_email_user_setting(self):
    #    """ test email notification user setting """
    #    n = Notification(
    #        to_user_id=1,
    #        from_user_id=2,
    #        type=NOTIFICATION_TYPES['friend_request_received'],
    #        description=NOTIFICATION_DESCRIPTIONS['friend_request_received'] % 'user1'
    #    )
    #    n.to_user.emailnotification.friend_request_received = False
    #    n.to_user.emailnotification.save()
    #    self.assertFalse(n.send_email(), 'should not send email')
    #    self.assertEqual(len(mail.outbox), 0)
    #    n.to_user.emailnotification.friend_request_received = True
    #    n.to_user.emailnotification.save()
    #    self.assertTrue(n.send_email(), 'should send email')
    #    self.assertEqual(len(mail.outbox), 1)
    #
    #def test_admin(self):
    #    self.client.login(username='admin', password='testuser1')
    #    
    #    # add 1 notification
    #    n = Notification(
    #        to_user_id=1,
    #        from_user_id=4,
    #        type=NOTIFICATION_TYPES['friend_request_received'],
    #        description=NOTIFICATION_DESCRIPTIONS['friend_request_received'] % 'user1'
    #    )
    #    n.save()
    #    
    #    # should get list
    #    response = self.client.get(reverse('admin:notification_notification_changelist'))
    #    self.assertContains(response, 'notification', msg_prefix='should get admin notification list page')
    #    # should get add
    #    response = self.client.get(reverse('admin:notification_notification_add'))
    #    self.assertEqual(response.status_code, 200, 'should get admin notification add')
    #    # should get change
    #    response = self.client.get(reverse('admin:notification_notification_change', args=[n.id]))
    #    self.assertEqual(response.status_code, 200, 'should get admin notification change page')
    #    # should get delete
    #    response = self.client.get(reverse('admin:notification_notification_delete', args=[n.id]))
    #    self.assertEqual(response.status_code, 200, 'should get admin notification delete page')
    #    # emailnotification and mobilenotification