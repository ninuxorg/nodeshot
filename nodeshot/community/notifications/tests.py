from django.test.client import Client
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.core import mail
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()

from nodeshot.core.base.tests import user_fixtures, BaseTestCase
from nodeshot.core.nodes.models import Node

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
            type='custom',
            text='test'
        )
        self.assertRaises(ValidationError, n.full_clean)
    
    def test_email_is_sent(self):
        """ Test custom notification is sent via email """
        n = Notification(
            to_user_id=1,
            from_user_id=2,
            type='custom',
            text='testing test'
        )
        n.save()
        
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
    
    if 'nodeshot.community.notifications.registrars.nodes' in settings.NODESHOT['NOTIFICATIONS']['REGISTRARS']:
        def test_node_created_to_all(self):
            # set every user to receive notifications about any node created
            all_users = User.objects.all()
            
            for user in all_users:
                user.email_notification_settings.node_created = 0
                user.email_notification_settings.save()
                user.web_notification_settings.node_created = 0
                user.web_notification_settings.save()
            
            node = Node.objects.create(**{
                'name': 'test notification',
                'slug': 'test-notification',
                'layer_id': 1,
                'geometry': 'POINT (-2.46 48.12)',
                'user_id': 1
            })
            
            # ensure all users except node owner have been notified about the node creation
            self.assertEqual(Notification.objects.count(), all_users.count()-1)
            self.assertEqual(len(mail.outbox), all_users.count()-1)
            
            # ensure owner notification object for owner has not been created in DB
            self.assertEqual(Notification.objects.filter(to_user_id=1).count(), 0)
        
        def test_node_created_to_noone(self):
            # set every user to NOT receive notifications about new nodes
            all_users = User.objects.all()
            
            for user in all_users:
                user.email_notification_settings.node_created = -1
                user.email_notification_settings.save()
                user.web_notification_settings.node_created = -1
                user.web_notification_settings.save()
            
            node = Node.objects.create(**{
                'name': 'test notification',
                'slug': 'test-notification',
                'layer_id': 1,
                'geometry': 'POINT (-2.46 48.12)',
                'user_id': 1
            })
            
            # ensure no notifications are created in the DB nor sent
            self.assertEqual(Notification.objects.count(), 0)
            self.assertEqual(len(mail.outbox), 0)
            
            # web notifications enabled
            for user in all_users:
                user.web_notification_settings.node_created = 0
                user.web_notification_settings.save()
            
            node = Node.objects.create(**{
                'name': 'test notification 2',
                'slug': 'test-notification 2',
                'layer_id': 1,
                'geometry': 'POINT (-2.16 47.12)',
                'user_id': 1
            })
            
            # ensure notifications are created
            self.assertEqual(Notification.objects.count(), all_users.count()-1)
            # but emails not sent
            self.assertEqual(len(mail.outbox), 0)
        
        def test_node_created_distance(self):
            # delete all the nodes
            Node.objects.all().delete()
            # mail counter
            mail_count = len(mail.outbox)
            # delete all notifications
            Notification.objects.all().delete()
            # set every user to NOT receive notifications about new nodes
            all_users = User.objects.all()
            
            # disable email notifications for all users
            for user in all_users:
                user.email_notification_settings.node_created = -1
                user.email_notification_settings.save()
                user.web_notification_settings.node_created = -1
                user.web_notification_settings.save()
            
            # enable notification in distance range only for romano
            user = User.objects.get(username='romano')
            user.email_notification_settings.node_created = 20  # 20 km
            user.email_notification_settings.save()
            user.web_notification_settings.node_created = 20
            user.web_notification_settings.save()
            
            node = Node.objects.create(**{
                'name': 'test notification',
                'slug': 'test-notification',
                'layer_id': 1,
                'geometry': 'POINT (12.5454 41.8352)',
                'user_id': 1
            })
            
            # ensure 1 email is sent
            self.assertEqual(len(mail.outbox), mail_count+1)
            # ensure 1 notification is created
            self.assertEqual(Notification.objects.count(), 1)
            
            node = Node.objects.create(**{
                'name': 'too far',
                'slug': 'too far',
                'layer_id': 1,
                'geometry': 'POINT (13.100 41.401)',
                'user_id': 1
            })
            
            # ensure no more notifications are created nor email sent
            self.assertEqual(Notification.objects.count(), 1)
            self.assertEqual(len(mail.outbox), mail_count+1)