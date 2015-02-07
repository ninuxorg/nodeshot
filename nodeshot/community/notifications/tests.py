import simplejson as json

from django.test.client import Client
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.core import mail, management
from django.contrib.auth import get_user_model
User = get_user_model()

from nodeshot.core.base.tests import user_fixtures, BaseTestCase
from nodeshot.core.base.utils import ago
from nodeshot.core.nodes.models import Node

from .models import *
from .settings import settings, DEFAULT_DISTANCE, DEFAULT_BOOLEAN, REGISTER
from .tasks import purge_notifications

# TODO: cleanup this mess
# remove websockets from installed apps and disconnect signals
if 'nodeshot.core.websockets' in settings.INSTALLED_APPS:
    from importlib import import_module
    from nodeshot.core.websockets import settings as websocket_settings

    for module in websocket_settings.REGISTER:
        module = import_module(module)
        module.disconnect()

    setattr(websocket_settings, 'REGISTER', [])

    settings.INSTALLED_APPS = [app for app in settings.INSTALLED_APPS if app != 'nodeshot.core.websockets']


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

    def setUp(self):
        # empty outbox, emails generated from EmailAddress model in nodeshot.community.profiles
        mail.outbox = []

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

        email_text = n.email_message
        self.assertIn('Hi', email_text)
        self.assertIn('testing test', email_text)
        self.assertIn('More details here', email_text)
        self.assertIn('This is an automatic notification sent from from', email_text)

    def test_purge_notifications(self):
        n = Notification.objects.create(**{
            "to_user_id": 1,
            "type": "custom",
            "text": "testing"
        })
        # not enough old to be purged
        n.added = ago(days=3)
        n.save(auto_update=False)
        management.call_command('purge_notifications')
        # no notifications have been deleted
        self.assertEqual(Notification.objects.count(), 1)

        # enough old to be purged
        n.added = ago(days=41)
        n.save(auto_update=False)
        management.call_command('purge_notifications')
        self.assertEqual(Notification.objects.count(), 0)

        n = Notification.objects.create(**{
            "to_user_id": 1,
            "type": "custom",
            "text": "testing"
        })
        n.added = ago(days=41)
        n.save(auto_update=False)
        purge_notifications.delay()
        self.assertEqual(Notification.objects.count(), 0)

    if 'nodeshot.community.notifications.registrars.nodes' in REGISTER:
        def test_check_settings(self):
            n = Notification(**{
                "to_user_id": 4,
                "type": "node_own_status_changed",
            })
            self.assertEqual(n.check_user_settings(medium='web'), DEFAULT_BOOLEAN)
            self.assertTrue(n.check_user_settings(medium='email'), DEFAULT_DISTANCE)

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

        def test_node_created_to_all_web_noone_mail(self):
            all_users = User.objects.all()

            for user in all_users:
                # no one wants to receive emails
                user.email_notification_settings.node_created = -1
                user.email_notification_settings.save()
                # everyone wants to receive web notifications about all nodes
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
            self.assertEqual(len(mail.outbox), 0)

            # ensure owner notification object for owner has not been created in DB
            self.assertEqual(Notification.objects.filter(to_user_id=1).count(), 0)

        def test_node_created_to_all_email_noone_web(self):
            all_users = User.objects.all()

            for user in all_users:
                # no one wants to receive emails
                user.email_notification_settings.node_created = 0
                user.email_notification_settings.save()
                # everyone wants to receive web notifications about all nodes
                user.web_notification_settings.node_created = -1
                user.web_notification_settings.save()

            node = Node.objects.create(**{
                'name': 'test notification',
                'slug': 'test-notification',
                'layer_id': 1,
                'geometry': 'POINT (-2.46 48.12)',
                'user_id': 1
            })

            # ensure all users except node owner have been notified about the node creation
            self.assertEqual(Notification.objects.count(), 0)
            self.assertEqual(len(mail.outbox), all_users.count()-1)

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
            # set every user to NOT receive notifications about new nodes
            # disable email notifications for all users
            for user in User.objects.all():
                user.email_notification_settings.node_created = -1
                user.email_notification_settings.node_deleted = -1
                user.email_notification_settings.save()
                user.web_notification_settings.node_created = -1
                user.web_notification_settings.node_deleted = -1
                user.web_notification_settings.save()

            # creat node of user who will receive the notification
            fusolab = Node.objects.create(**{
                'name': 'a node in rome',
                'slug': 'a-node-in-rome',
                'layer_id': 1,
                'geometry': 'POINT (12.5822391919000012 41.8720419276999820)',
                'user_id': 4  # romano
            })
            # ensure no notifications have been created/sent
            self.assertEqual(len(mail.outbox), 0)
            self.assertEqual(Notification.objects.count(), 0)

            # enable notification in distance range only for romano
            user = User.objects.get(username='romano')
            user.email_notification_settings.node_created = 20  # 20 km
            user.email_notification_settings.save()
            user.web_notification_settings.node_created = 20
            user.web_notification_settings.save()

            # romano should receive a notification when this new near node is created
            near_node = Node.objects.create(**{
                'name': 'test notification',
                'slug': 'test-notification',
                'layer_id': 1,
                'geometry': 'POINT (12.5454 41.8352)',
                'user_id': 1
            })

            # ensure 1 email is sent
            self.assertEqual(len(mail.outbox), 1)
            # ensure 1 notification is created
            self.assertEqual(Notification.objects.count(), 1)
            # ensure notification is directed towards him
            notification = Notification.objects.all().order_by('-id')[0]
            self.assertEqual(notification.to_user_id, 4)

            # a new node is created at a distance wich is too far for romano's preferences
            far_node = Node.objects.create(**{
                'name': 'too far',
                'slug': 'too far',
                'layer_id': 1,
                'geometry': 'POINT (13.100 41.401)',
                'user_id': 1
            })

            # ensure no notifications are created nor email sent
            self.assertEqual(Notification.objects.count(), 1)
            self.assertEqual(len(mail.outbox), 1)

            # RESET
            near_node.delete()
            far_node.delete()
            Notification.objects.all().delete()

            # romano now wants to be notified via email but doesn't want to see the web notification
            user.email_notification_settings.node_created = 20  # 20 km
            user.email_notification_settings.save()
            user.web_notification_settings.node_created = -1
            user.web_notification_settings.save()

            near_node = Node.objects.create(**{
                'name': 'test notification',
                'slug': 'test-notification',
                'layer_id': 1,
                'geometry': 'POINT (12.5454 41.8352)',
                'user_id': 1
            })
            # ensure 1 email is sent
            self.assertEqual(len(mail.outbox), 2)
            # ensure 1 notification is created
            self.assertEqual(Notification.objects.count(), 0)

        def test_node_deleted_all(self):
            # set every user to receive notifications about any node deletion
            all_users = User.objects.all()

            for user in all_users:
                user.email_notification_settings.node_deleted = 0
                user.email_notification_settings.node_created = -1
                user.email_notification_settings.save()
                user.web_notification_settings.node_deleted = 0
                user.web_notification_settings.node_created = -1
                user.web_notification_settings.save()

            node = Node.objects.create(**{
                'name': 'test notification',
                'slug': 'test-notification',
                'layer_id': 1,
                'geometry': 'POINT (-2.46 48.12)',
                'user_id': 1
            })
            # ensure 0 notifications
            self.assertEqual(Notification.objects.count(), 0)
            self.assertEqual(len(mail.outbox), 0)

            node.delete()

            self.assertEqual(Notification.objects.count(), all_users.count()-1)
            self.assertEqual(len(mail.outbox), all_users.count()-1)

        def test_node_deleted_all_email_noone_web(self):
            all_users = User.objects.all()

            for user in all_users:
                user.email_notification_settings.node_deleted = 0
                user.email_notification_settings.node_created = -1
                user.email_notification_settings.save()
                user.web_notification_settings.node_deleted = -1
                user.web_notification_settings.node_created = -1
                user.web_notification_settings.save()

            node = Node.objects.create(**{
                'name': 'test notification',
                'slug': 'test-notification',
                'layer_id': 1,
                'geometry': 'POINT (-2.46 48.12)',
                'user_id': 1
            })
            # ensure 0 notifications
            self.assertEqual(Notification.objects.count(), 0)
            self.assertEqual(len(mail.outbox), 0)

            node.delete()

            self.assertEqual(Notification.objects.count(), 0)
            self.assertEqual(len(mail.outbox), all_users.count()-1)

        def test_node_deleted_all_web_noone_email(self):
            all_users = User.objects.all()

            for user in all_users:
                user.email_notification_settings.node_deleted = -1
                user.email_notification_settings.node_created = -1
                user.email_notification_settings.save()
                user.web_notification_settings.node_deleted = 0
                user.web_notification_settings.node_created = -1
                user.web_notification_settings.save()

            node = Node.objects.create(**{
                'name': 'test notification',
                'slug': 'test-notification',
                'layer_id': 1,
                'geometry': 'POINT (-2.46 48.12)',
                'user_id': 1
            })
            # ensure 0 notifications
            self.assertEqual(Notification.objects.count(), 0)
            self.assertEqual(len(mail.outbox), 0)

            node.delete()

            self.assertEqual(Notification.objects.count(), all_users.count()-1)
            self.assertEqual(len(mail.outbox), 0)

        def test_node_deleted_distance(self):
            # set every user to NOT receive notifications about new nodes
            # disable email notifications for all users
            for user in User.objects.all():
                user.email_notification_settings.node_created = -1
                user.email_notification_settings.node_deleted = -1
                user.email_notification_settings.save()
                user.web_notification_settings.node_created = -1
                user.web_notification_settings.node_deleted = -1
                user.web_notification_settings.save()

            # create node of user who will receive the notification
            fusolab = Node.objects.create(**{
                'name': 'a node in rome',
                'slug': 'a-node-in-rome',
                'layer_id': 1,
                'geometry': 'POINT (12.5822391919000012 41.8720419276999820)',
                'user_id': 4  # romano
            })

            # enable notification in distance range only for romano
            user = User.objects.get(username='romano')
            user.email_notification_settings.node_deleted = 20  # 20 km
            user.email_notification_settings.save()
            user.web_notification_settings.node_deleted = 20
            user.web_notification_settings.save()

            # romano should receive a notification when this new near node is created
            near_node = Node.objects.create(**{
                'name': 'test notification',
                'slug': 'test-notification',
                'layer_id': 1,
                'geometry': 'POINT (12.5454 41.8352)',
                'user_id': 1
            })

            # ensure 0 notifications
            self.assertEqual(len(mail.outbox), 0)
            self.assertEqual(Notification.objects.count(), 0)

            # delete node
            near_node.delete()

            # ensure 1 email is sent
            self.assertEqual(len(mail.outbox), 1)
            # ensure 1 notification is created
            self.assertEqual(Notification.objects.count(), 1)
            # ensure notification is directed towards him
            notification = Notification.objects.all().order_by('-id')[0]
            self.assertEqual(notification.to_user_id, 4)

            # a new node is created at a distance wich is too far for romano's preferences
            far_node = Node.objects.create(**{
                'name': 'too far',
                'slug': 'too far',
                'layer_id': 1,
                'geometry': 'POINT (13.100 41.401)',
                'user_id': 1
            })

            # ensure 0 notifications
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(Notification.objects.count(), 1)

            far_node.delete()

            # ensure no additional notifications are created nor email sent
            self.assertEqual(Notification.objects.count(), 1)
            self.assertEqual(len(mail.outbox), 1)

            # RESET
            Notification.objects.all().delete()

            # romano now wants to be notified via email but doesn't want to see the web notification
            user.email_notification_settings.node_deleted = 20  # 20 km
            user.email_notification_settings.save()
            user.web_notification_settings.node_deleted = -1
            user.web_notification_settings.save()

            near_node = Node.objects.create(**{
                'name': 'test notification',
                'slug': 'test-notification',
                'layer_id': 1,
                'geometry': 'POINT (12.5454 41.8352)',
                'user_id': 1
            })
            near_node.delete()
            # ensure 1 email is sent
            self.assertEqual(len(mail.outbox), 2)
            # ensure 1 notification is created
            self.assertEqual(Notification.objects.count(), 0)

            # RESET
            Notification.objects.all().delete()

            # yes to web no to email
            user.email_notification_settings.node_deleted = -1
            user.email_notification_settings.save()
            user.web_notification_settings.node_deleted = 20
            user.web_notification_settings.save()

            near_node = Node.objects.create(**{
                'name': 'test notification',
                'slug': 'test-notification',
                'layer_id': 1,
                'geometry': 'POINT (12.5454 41.8352)',
                'user_id': 1
            })
            near_node.delete()
            # no additional mail sent
            self.assertEqual(len(mail.outbox), 2)
            # ensure 1 notification is created
            self.assertEqual(Notification.objects.count(), 1)
            # ensure notification is directed towards him
            notification = Notification.objects.all().order_by('-id')[0]
            self.assertEqual(notification.to_user_id, 4)

        def test_node_status_changed_all(self):
            all_users = User.objects.all()

            # all users receive notifications about status changes but no other notification
            for user in all_users:
                user.email_notification_settings.node_deleted = -1
                user.email_notification_settings.node_created = -1
                user.email_notification_settings.node_status_changed = 0
                user.email_notification_settings.save()
                user.web_notification_settings.node_deleted = -1
                user.web_notification_settings.node_created = -1
                user.web_notification_settings.node_status_changed = 0
                user.web_notification_settings.save()

            node = Node.objects.create(**{
                'name': 'test notification',
                'slug': 'test-notification',
                'layer_id': 1,
                'geometry': 'POINT (-2.46 48.12)',
                'user_id': 1
            })
            # ensure 0 notifications
            self.assertEqual(Notification.objects.count(), 0)
            self.assertEqual(len(mail.outbox), 0)

            node.status_id = 3
            node.save()

            self.assertEqual(Notification.objects.filter(type='node_status_changed').count(), all_users.count()-1)
            self.assertEqual(Notification.objects.filter(type='node_own_status_changed').count(), 1)
            # ensure notification of type "node_own_status_changed" is directed towards owner
            notification = Notification.objects.filter(type='node_own_status_changed').order_by('-id')[0]
            self.assertEqual(notification.to_user_id, 1)
            self.assertEqual(len(mail.outbox), 8)  # all users have received emails

        def test_node_status_changed_all_email_noone_web(self):
            all_users = User.objects.all()

            for user in all_users:
                user.email_notification_settings.node_deleted = -1
                user.email_notification_settings.node_created = -1
                user.email_notification_settings.node_status_changed = 0
                user.email_notification_settings.save()
                user.web_notification_settings.node_deleted = -1
                user.web_notification_settings.node_created = -1
                user.web_notification_settings.node_status_changed = -1
                user.web_notification_settings.save()

            node = Node.objects.create(**{
                'name': 'test notification',
                'slug': 'test-notification',
                'layer_id': 1,
                'geometry': 'POINT (-2.46 48.12)',
                'user_id': 1
            })
            # ensure 0 notifications
            self.assertEqual(Notification.objects.count(), 0)
            self.assertEqual(len(mail.outbox), 0)

            node.status_id = 3
            node.save()

            self.assertEqual(Notification.objects.filter(type='node_status_changed').count(), 0)
            self.assertEqual(Notification.objects.filter(type='node_own_status_changed').count(), 1)
            # ensure notification of type "node_own_status_changed" is directed towards owner
            notification = Notification.objects.filter(type='node_own_status_changed').order_by('-id')[0]
            self.assertEqual(notification.to_user_id, 1)
            self.assertEqual(len(mail.outbox), 8)  # all users have received emails

        def test_node_status_changed_distance(self):
            all_users = User.objects.all()

            # disable everything
            for user in all_users:
                user.email_notification_settings.node_deleted = -1
                user.email_notification_settings.node_created = -1
                user.email_notification_settings.node_status_changed = -1
                user.email_notification_settings.node_own_status_changed = False
                user.email_notification_settings.save()
                user.web_notification_settings.node_deleted = -1
                user.web_notification_settings.node_created = -1
                user.web_notification_settings.node_status_changed = -1
                user.web_notification_settings.node_own_status_changed = False
                user.web_notification_settings.save()

            # create node of user who will receive the notification
            fusolab = Node.objects.create(**{
                'name': 'a node in rome',
                'slug': 'a-node-in-rome',
                'layer_id': 1,
                'geometry': 'POINT (12.5822391919000012 41.8720419276999820)',
                'user_id': 4  # romano
            })
            # ensure 0 notifications
            self.assertEqual(Notification.objects.count(), 0)
            self.assertEqual(len(mail.outbox), 0)

            # enable notification in distance range only for romano
            user = User.objects.get(username='romano')
            user.email_notification_settings.node_status_changed = 20  # 20 km
            user.email_notification_settings.save()
            user.web_notification_settings.node_status_changed = 20
            user.web_notification_settings.save()

            # romano should receive a notification when this new near node is created
            near_node = Node.objects.create(**{
                'name': 'test notification',
                'slug': 'test-notification',
                'layer_id': 1,
                'geometry': 'POINT (12.5454 41.8352)',
                'user_id': 1
            })
            # ensure 0 notifications
            self.assertEqual(Notification.objects.count(), 0)
            self.assertEqual(len(mail.outbox), 0)

            near_node.status_id = 3
            near_node.save()

            # ensure 1 email is sent
            self.assertEqual(len(mail.outbox), 1)
            # ensure 1 notification is created
            self.assertEqual(Notification.objects.count(), 1)
            self.assertEqual(Notification.objects.filter(type='node_status_changed').count(), 1)
            # ensure notification is directed towards romano
            notification = Notification.objects.all().order_by('-id')[0]
            self.assertEqual(notification.to_user_id, 4)

            # a new node is created at a distance wich is too far for romano's preferences
            far_node = Node.objects.create(**{
                'name': 'too far',
                'slug': 'too far',
                'layer_id': 1,
                'geometry': 'POINT (13.100 41.401)',
                'user_id': 1
            })

            far_node.status_id = 3
            far_node.save()

            # ensure no additional notifications are created nor email sent
            self.assertEqual(Notification.objects.count(), 1)
            self.assertEqual(len(mail.outbox), 1)

            # RESET
            near_node.delete()
            far_node.delete()
            Notification.objects.all().delete()

            # romano now wants to be notified via email but doesn't want to see the web notification
            user.email_notification_settings.node_status_changed = 20  # 20 km
            user.email_notification_settings.save()
            user.web_notification_settings.node_status_changed = -1
            user.web_notification_settings.save()

            near_node = Node.objects.create(**{
                'name': 'test notification',
                'slug': 'test-notification',
                'layer_id': 1,
                'geometry': 'POINT (12.5454 41.8352)',
                'user_id': 1
            })

            near_node.status_id = 3
            near_node.save()

            # ensure 1 email is sent
            self.assertEqual(len(mail.outbox), 2)
            # ensure 1 notification is created
            self.assertEqual(Notification.objects.count(), 0)

        def test_read_notifications_API(self):
            """ test read notification API operation """
            url = reverse('api_notification_list')

            # GET 403 unauthorized
            response = self.client.get(url)
            self.assertEqual(response.status_code, 403)

            self.client.login(username='romano', password='tester')

            response = self.client.get(url)
            self.assertContains(response, '[]')

            user = User.objects.get(pk=4)
            user.web_notification_settings.node_created = 0
            user.web_notification_settings.save()

            # generate a notification
            fusolab = Node.objects.create(**{
                'name': 'a node in rome',
                'slug': 'a-node-in-rome',
                'layer_id': 1,
                'geometry': 'POINT (12.5822391919000012 41.8720419276999820)',
                'user_id': 1  # admin
            })

            # test ?action=count
            response = self.client.get(url, { 'action': 'count' })
            self.assertContains(response, '{"count": 1}')

            # test ?read=false
            # retrieve notifications but do not mark as read
            response = self.client.get(url, { 'read': 'false' })
            self.assertEquals(1, len(response.data), 'expected 1 notification')

            # test ?read=true
            # repeating the request should still show 1 unread notification, but the read operation will mark them as read
            self.assertEqual(Notification.objects.filter(to_user_id=4, is_read=False).count(), 1)
            response = self.client.get(url)
            self.assertEquals(1, len(response.data))
            # repeating again should find 0 unread notifications
            response = self.client.get(url)
            self.assertContains(response, '[]')
            self.assertEqual(Notification.objects.filter(to_user_id=4, is_read=False).count(), 0)

            # test action=all
            response = self.client.get(url, { 'action': 'all' })
            notifications = response.data
            self.assertEquals(1, len(notifications['results']))
            self.assertContains(response, '"is_read"', msg_prefix="'read' should be a field on its own")

            # test pagination of action=all
            for i in range(1, 31):
                notification_text = 'testing notifications, iteration n. %d' % i
                n = Notification(
                    to_user_id=4,
                    type='custom',
                    text=notification_text
                )
                n.save()
            response = self.client.get(url, { 'action': 'all' })
            notifications = response.data
            self.assertEquals(31, notifications['count'])
            self.assertTrue(notifications['next'] is not None, 'expected a next page')
            self.assertTrue(notifications['previous'] is None, 'expected no previous page')
            response = self.client.get(notifications['next'])
            notifications = response.data
            self.assertTrue(notifications['previous'] is not None, 'expected a previous page')

            # test non expected action should default to unread
            response = self.client.get(url, { 'action': 'doesntexist' })
            self.assertEquals(30, len(response.data))

        def test_notification_detail_API(self):
            # set user #4 to receive notifications
            user = User.objects.get(pk=4)
            user.web_notification_settings.node_created = 0
            user.web_notification_settings.save()

            # generate a notification
            fusolab = Node.objects.create(**{
                'name': 'a node in rome',
                'slug': 'a-node-in-rome',
                'layer_id': 1,
                'geometry': 'POINT (12.5822391919000012 41.8720419276999820)',
                'user_id': 1  # admin
            })

            notification_id = Notification.objects.order_by('-id').all()[0].id

            # test notification detail
            url = reverse('api_notification_detail', args=[notification_id])

            # GET 403 unauthorized
            response = self.client.get(url)
            self.assertEqual(response.status_code, 403)

            # GET 404
            # login as wrong user
            self.client.login(username='registered', password='tester')
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)
            self.client.logout()

            # GET 200
            # login as right user
            self.client.login(username='romano', password='tester')
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['id'], notification_id)

        def test_email_notification_settings(self):
            """ ensure email notification settings endpoint works correctly """
            url = reverse('api_notification_email_settings')

            # GET 401: unauthenticated request should fail
            c = Client()
            response = c.get(url)
            self.assertContains(response, 'credentials', status_code=403)

            self.client.login(username='romano', password='tester')

            # GET 200
            response = self.client.get(url)
            self.assertEquals(200, response.status_code)
            self.assertContains(response, 'uri')
            self.assertContains(response, 'node_created')
            self.assertContains(response, 'node_status_changed')
            self.assertContains(response, 'node_own_status_changed')
            self.assertContains(response, 'node_deleted')

            # PATCH 200
            response = self.client.patch(url, { "node_own_status_changed": False })
            self.assertEquals(200, response.status_code)
            # check DB
            user = User.objects.get(username='romano')
            self.assertFalse(user.email_notification_settings.node_own_status_changed)

            # PUT 200
            response = self.client.put(url, json.dumps({
                "node_created": 50,
                "node_status_changed": 50,
                "node_own_status_changed": True,
                "node_deleted": 50
            }), content_type='application/json')
            self.assertEquals(200, response.status_code)
            # check DB
            user = User.objects.get(username='romano')
            self.assertTrue(user.email_notification_settings.node_own_status_changed)
            self.assertEqual(user.email_notification_settings.node_created, 50)
            self.assertEqual(user.email_notification_settings.node_status_changed, 50)
            self.assertEqual(user.email_notification_settings.node_deleted, 50)

        def test_web_notification_settings(self):
            """ ensure web notification settings endpoint works correctly """
            url = reverse('api_notification_web_settings')

            # GET 401: unauthenticated request should fail
            c = Client()
            response = c.get(url)
            self.assertContains(response, 'credentials', status_code=403)

            self.client.login(username='romano', password='tester')

            # GET 200
            response = self.client.get(url)
            self.assertEquals(200, response.status_code)
            self.assertContains(response, 'uri')
            self.assertContains(response, 'node_created')
            self.assertContains(response, 'node_status_changed')
            self.assertContains(response, 'node_own_status_changed')
            self.assertContains(response, 'node_deleted')

            # PATCH 200
            response = self.client.patch(url, { "node_own_status_changed": False })
            self.assertEquals(200, response.status_code)
            # check DB
            user = User.objects.get(username='romano')
            self.assertFalse(user.web_notification_settings.node_own_status_changed)

            # PUT 200
            response = self.client.put(url, json.dumps({
                "node_created": 50,
                "node_status_changed": 50,
                "node_own_status_changed": True,
                "node_deleted": 50
            }), content_type='application/json')
            self.assertEquals(200, response.status_code)
            # check DB
            user = User.objects.get(username='romano')
            self.assertTrue(user.web_notification_settings.node_own_status_changed)
            self.assertEqual(user.web_notification_settings.node_created, 50)
            self.assertEqual(user.web_notification_settings.node_status_changed, 50)
            self.assertEqual(user.web_notification_settings.node_deleted, 50)
