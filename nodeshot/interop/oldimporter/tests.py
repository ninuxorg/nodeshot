from django.test import TestCase
from django.core import mail, management
from django.contrib.gis.geos import Point

from nodeshot.core.nodes.models import Node
from nodeshot.core.layers.models import Layer
from nodeshot.networking.net.models import Device, Interface, Ip, Vap, Wireless
from nodeshot.networking.links.models import Link
from nodeshot.community.profiles.models import Profile as User
from nodeshot.community.profiles.models import EmailAddress, EmailConfirmation
from nodeshot.community.mailing.models import Inward

from .models import *  # noqa
from . import settings


class TestOldImporter(TestCase):
    fixtures = [
        'initial_data.json',
        'test_profiles.json',
        'test_layers.json',
        'test_status.json',
    ]

    mysql_fixtures = [
        'test_oldusers.json',
        'test_oldnodes.json',
        'test_olddevices.json',
        'test_oldlinks.json',
        'test_oldcontacts.json'
    ]

    def setUp(self):
        for fixture in self.mysql_fixtures:
            management.call_command('loaddata', fixture, database='old_nodeshot')

        # setup layer 1 and 2 area
        l1 = Layer.objects.get(pk=1)
        l1.area = 'POLYGON ((11.9727761230500001 42.0001370328649983, 12.3188454589879992 42.2669596835330026, 12.9148537597690005 42.1509994246999966, 13.2609230957069997 41.8079840923359995, 12.7500588378940005 41.3951648168940025, 12.5962502441440005 41.4445954826359966, 12.4067360839879992 41.6501514845399967, 12.1925026855510001 41.7444877274350006, 12.1128518066440005 41.9184405084070022, 12.0277077636760001 41.9368313579400009, 12.0277077636760001 41.9429604629400004, 11.9727761230500001 42.0001370328649983))'
        l1.save()

        l2 = l1 = Layer.objects.get(pk=2)
        l2.area = 'POLYGON ((10.1833779296829992 43.9387627493410022, 10.3454262695289998 43.9901623726480011, 10.6475502929680008 43.9822576330009980, 10.7491738281280007 43.9071101075910022, 10.8205849609349993 43.7188257293139984, 10.7574135742189991 43.5558293167039992, 10.6283242187470002 43.3484662663620028, 10.4470498046879996 43.3344836017819972, 10.3591591796899998 43.4602116419999973, 10.2712685546909999 43.5518482711390007, 10.2575356445299999 43.6830839058609968, 10.2383095703089992 43.8338488741229995, 10.1751381835920007 43.9328291618219993, 10.1833779296829992 43.9387627493410022))'
        l2.save()

        l = Layer()
        l.id = 5
        l.name = 'Default Layer'
        l.slug = 'default-layer'
        l.description = 'Default Layer'
        l.organization = 'Test'
        l.published = True
        l.area = Point(40.0, 10.0)
        l.full_clean()
        l.save()

    def test_command(self):
        for user in User.objects.all():
            user.delete()

        settings.DEFAULT_LAYER = 5
        management.call_command('import_old_nodeshot', noinput=True)

        nodes = Node.objects.all().order_by('id')
        devices = Device.objects.all().order_by('id')
        interfaces = Interface.objects.all().order_by('id')
        ip_addresses = Ip.objects.all().order_by('id')
        links = Link.objects.all().order_by('id')
        users = User.objects.all()
        email_addresses = EmailAddress.objects.all()
        email_confirmations = EmailConfirmation.objects.all()
        inwards = Inward.objects.all()

        self.assertEqual(len(nodes), 5)
        self.assertEqual(len(devices), 2)
        self.assertEqual(len(interfaces), 4)
        self.assertEqual(len(ip_addresses), 8)
        self.assertEqual(Vap.objects.count(), 2)
        self.assertEqual(len(links), 1)
        self.assertEqual(len(users), 6)
        self.assertEqual(len(email_addresses), 6)
        self.assertEqual(len(email_confirmations), 0)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(len(inwards), 1)

        # admin check
        self.assertEqual(User.objects.filter(is_staff=True).count(), 2)
        self.assertEqual(User.objects.filter(is_superuser=True).count(), 1)
        superuser = User.objects.filter(is_superuser=True).first()
        self.assertEqual(superuser.email, 'oldnode1@test.com')
        self.assertEqual(superuser.is_staff, True)
        self.assertEqual(superuser.password, 'md5$C2xwUqHfBz4P$f37f9e6f4f076b1239a5c5dff2c8a2ab')
        # staff user
        randomuser = User.objects.get(username='randomuser')
        self.assertEqual(randomuser.email, 'random@test.com')
        self.assertEqual(randomuser.is_staff, True)
        self.assertEqual(randomuser.is_superuser, False)
        self.assertEqual(randomuser.password, 'md5$C2xwUqHfBz4P$f37f9e6f4f076b1239a5c5dff2c8a2ac')
        # date joined check
        self.assertEqual(randomuser.date_joined.strftime('%Y-%m-%dT%H:%M:%S'), '2013-05-18T13:36:47')

        # node1
        self.assertEqual(nodes[0].id, 1)
        self.assertEqual(nodes[0].name, 'oldnode1 rome')
        self.assertEqual(nodes[0].slug, 'oldnode1-rome')
        self.assertEqual(nodes[0].user.get_full_name(), 'Oldnode1 Owner')
        self.assertEqual(nodes[0].user.username, 'oldnode1-owner')
        self.assertEqual(nodes[0].user.email, 'oldnode1@test.com')
        self.assertEqual(nodes[0].description, 'oldnode1-description')
        self.assertEqual(nodes[0].data['postal_code'], '00185')
        self.assertEqual(nodes[0].status.slug, 'active')
        self.assertEqual(nodes[0].updated.strftime('%Y-%m-%dT%H:%M:%S'), '2013-06-20T13:36:47')
        self.assertEqual(nodes[0].added.strftime('%Y-%m-%dT%H:%M:%S'), '2013-06-14T13:30:29')
        self.assertEqual(nodes[0].geometry[0], 12.5390629470348003)
        self.assertEqual(nodes[0].geometry[1], 41.9064152946931969)
        self.assertEqual(nodes[0].elev, 24.5)
        # ensure layer has been picked correctly
        self.assertEqual(nodes[0].layer.slug, 'rome')
        # ensure owner date_joined is correct
        self.assertEqual(nodes[0].user.date_joined.strftime('%Y-%m-%dT%H:%M:%S'), '2013-06-14T13:30:29')

        # node2
        self.assertEqual(nodes[1].id, 2)
        self.assertEqual(nodes[1].name, 'oldnode2 rome')
        self.assertEqual(nodes[1].slug, 'oldnode2-rome')
        self.assertEqual(nodes[1].user.get_full_name(), 'Oldnode2 Owner')
        self.assertEqual(nodes[1].user.username, 'oldnode2-owner')
        self.assertEqual(nodes[1].user.email, 'oldnode2@test.com')
        self.assertEqual(nodes[1].description, 'oldnode2-description')
        self.assertEqual(nodes[1].data['postal_code'], '00175')
        self.assertEqual(nodes[1].data['is_hotspot'], 'true')
        self.assertEqual(nodes[1].status.slug, 'active')
        self.assertEqual(nodes[1].updated.strftime('%Y-%m-%dT%H:%M:%S'), '2013-06-19T13:36:47')
        self.assertEqual(nodes[1].added.strftime('%Y-%m-%dT%H:%M:%S'), '2013-06-19T13:30:29')
        self.assertEqual(nodes[1].geometry[0], 12.534556835889)
        self.assertEqual(nodes[1].geometry[1], 41.90746129417)
        self.assertEqual(nodes[1].elev, 15.5)
        # ensure layer has been picked correctly
        self.assertEqual(nodes[1].layer.slug, 'rome')
        # ensure owner date_joined is correct
        self.assertEqual(nodes[1].user.date_joined.strftime('%Y-%m-%dT%H:%M:%S'), '2013-06-19T13:30:29')

        # node3
        self.assertEqual(nodes[2].id, 3)
        self.assertEqual(nodes[2].name, 'oldnode3 pisa')
        self.assertEqual(nodes[2].slug, 'oldnode3-pisa')
        self.assertEqual(nodes[2].user.get_full_name(), 'Oldnode3 Pisano')
        self.assertEqual(nodes[2].user.username, 'oldnode3-pisano')
        self.assertEqual(nodes[2].user.email, 'oldnode3@test.com')
        self.assertEqual(nodes[2].description, 'oldnode3 description')
        self.assertEqual(nodes[2].data['postal_code'], '00100')
        self.assertEqual(nodes[2].status.slug, 'potential')
        self.assertEqual(nodes[2].updated.strftime('%Y-%m-%dT%H:%M:%S'), '2013-06-18T13:36:47')
        self.assertEqual(nodes[2].added.strftime('%Y-%m-%dT%H:%M:%S'), '2013-06-18T13:30:29')
        self.assertEqual(nodes[2].geometry[0], 10.3973981737999992)
        self.assertEqual(nodes[2].geometry[1], 43.7175764660999988)
        self.assertEqual(nodes[2].elev, 10)
        # ensure layer has been picked correctly
        self.assertEqual(nodes[2].layer.slug, 'pisa')
        # ensure owner date_joined is correct
        self.assertEqual(nodes[2].user.date_joined.strftime('%Y-%m-%dT%H:%M:%S'), '2013-06-18T13:30:29')

        # ensure default layer
        self.assertEqual(nodes[3].layer.slug, 'default-layer')
        self.assertEqual(nodes[3].layer.id, 5)

        # device import check
        self.assertEqual(devices[0].id, 1)
        self.assertEqual(devices[0].name, 'device1')
        self.assertEqual(devices[0].node_id, 1)
        self.assertEqual(devices[0].description, 'device1-description')
        self.assertEqual(devices[0].type, 'radio')
        self.assertEqual(devices[0].data['cname'], 'oldnode1-device1')
        self.assertEqual(devices[0].data['model'], 'test model')
        self.assertEqual(devices[0].added.strftime('%Y-%m-%dT%H:%M:%S'), '2013-08-14T13:30:29')
        self.assertEqual(devices[0].routing_protocols.count(), 1)
        self.assertEqual(devices[0].routing_protocols.first().name, 'olsr')

        # interface import check
        self.assertEqual(interfaces[0].id, 1)
        self.assertEqual(interfaces[0].device_id, 1)
        self.assertEqual(interfaces[0].mac, '00:27:22:38:d1:38')
        self.assertEqual(interfaces[0].name, 'eth')
        self.assertEqual(interfaces[0].get_type_display(), 'ethernet')
        self.assertEqual(interfaces[0].added.strftime('%Y-%m-%dT%H:%M:%S'), '2013-08-15T13:30:29')
        self.assertEqual(interfaces[0].ip_set.count(), 2)
        ipv4 = interfaces[0].ip_set.filter(protocol='ipv4').first()
        self.assertEqual(str(ipv4.address), '10.40.0.1')
        ipv6 = interfaces[0].ip_set.filter(protocol='ipv6').first()
        self.assertEqual(str(ipv6.address), '2001:4c00:893b:fede:eddb:decd:e878:88b3')

        # wireless interface check
        wireless_interface = Wireless.objects.get(pk=interfaces[1].id)
        self.assertEqual(wireless_interface.id, 2)
        self.assertEqual(wireless_interface.device_id, 1)
        self.assertEqual(wireless_interface.mac, '00:27:22:38:d1:39')
        self.assertEqual(wireless_interface.name, 'wifi')
        self.assertEqual(wireless_interface.get_type_display(), 'wireless')
        self.assertEqual(wireless_interface.channel, '5620')
        self.assertEqual(wireless_interface.mode, 'ap')
        self.assertEqual(wireless_interface.added.strftime('%Y-%m-%dT%H:%M:%S'), '2013-08-16T13:30:29')
        ipv4 = wireless_interface.ip_set.filter(protocol='ipv4').first()
        self.assertEqual(str(ipv4.address), '172.16.40.27')
        ipv6 = wireless_interface.ip_set.filter(protocol='ipv6').first()
        self.assertEqual(str(ipv6.address), '2001:4c00:893b:fede:eddb:decd:e878:88b4')

        # vap check
        vap = wireless_interface.vap_set.first()
        self.assertEqual(vap.essid, 'essid test')
        self.assertEqual(vap.bssid, 'bssidtest')

        # link check
        self.assertEqual(links[0].id, 1)
        self.assertEqual(links[0].interface_a_id, 2)
        self.assertEqual(links[0].interface_b_id, 4)
        self.assertEqual(links[0].metric_type, 'etx')
        self.assertEqual(links[0].metric_value, 1)
        self.assertEqual(links[0].dbm, -76)
        self.assertEqual(links[0].min_rate, 50)
        self.assertEqual(links[0].max_rate, 50)

        # inward contact check
        self.assertEqual(inwards[0].id, 1)
        self.assertEqual(inwards[0].object_id, 1)
        self.assertEqual(inwards[0].status, 1)
        self.assertEqual(inwards[0].from_name, 'Tester')
        self.assertEqual(inwards[0].from_email, 'tester@test.com')
        self.assertEqual(inwards[0].message, 'This is a test old contact')
        self.assertEqual(inwards[0].ip, '10.40.0.56')
        self.assertEqual(inwards[0].user_agent, 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/33.0.1750.152 Chrome/33.0.1750.152 Safari/537.36')
        self.assertEqual(inwards[0].accept_language, 'it-IT,it;q=0.8,en-US;q=0.6,en;q=0.4')
        self.assertEqual(inwards[0].added.strftime('%Y-%m-%dT%H:%M:%S'), '2013-09-14T13:30:29')

        # --- update --- #

        n = OldNode(**{
            "name": "addednode1",
            "slug": "addednode1",
            "owner": "addednode1 owner",
            "description": "addednode1-description",
            "postal_code": "00185",
            "email": "addednode@test.com",
            "password": "",
            "lat": 41.4064152946931969,
            "lng": 12.7390629470348003,
            "alt": 23.5,
            "status": "a"
        })
        n.save()

        d = OldDevice(**{
            "name": "addeddevice1",
            "node": n,
            "cname": "addeddevice1",
            "description": "addeddevice1-description",
            "type": "test model",
            "routing_protocol": "olsr"
        })
        d.save()

        i = OldInterface(**{
            "device": d,
            "mac_address": "00:27:22:38:D1:48",
            "ipv4_address": "10.40.0.6",
            "ipv6_address": "2001:4c00:893b:fede:eddb:decd:e878:88c3",
            "cname": "addedeth",
            "type": "eth",
            "status": "r"
        })
        i.save()

        l = OldLink(**{
            "from_interface": OldInterface.objects.first(),
            "to_interface": i,
            "etx": 1,
            "dbm": -75,
            "sync_tx": 60,
            "sync_rx": 40
        })
        l.save()

        c = OldContact(**{
            "node_id": 1,
            "from_name": "Added",
            "from_email": "added@test.com",
            "message": "This is an added test old contact",
            "ip": "10.40.0.57",
            "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/33.0.1750.152 Chrome/33.0.1750.152 Safari/537.36",
            "http_referer": "http://map.ninux.org/",
            "accept_language": "it-IT,it;q=0.8,en-US;q=0.6,en;q=0.4"
        })
        c.save()

        management.call_command('import_old_nodeshot', noinput=True)

        nodes = Node.objects.all().order_by('id')
        devices = Device.objects.all().order_by('id')
        interfaces = Interface.objects.all().order_by('id')
        ip_addresses = Ip.objects.all().order_by('id')
        links = Link.objects.all().order_by('id')
        users = User.objects.all().order_by('id')
        email_addresses = EmailAddress.objects.all()
        email_confirmations = EmailConfirmation.objects.all()
        inwards = Inward.objects.all().order_by('id')

        self.assertEqual(len(nodes), 6)
        self.assertEqual(len(devices), 3)
        self.assertEqual(len(interfaces), 5)
        self.assertEqual(len(ip_addresses), 10)
        self.assertEqual(Vap.objects.count(), 2)
        self.assertEqual(len(links), 2)
        self.assertEqual(len(users), 7)
        self.assertEqual(len(email_addresses), 7)
        self.assertEqual(len(email_confirmations), 0)
        self.assertEqual(len(inwards), 2)

        # admin check
        self.assertEqual(User.objects.filter(is_staff=True).count(), 2)
        self.assertEqual(User.objects.filter(is_superuser=True).count(), 1)

        self.assertEqual(nodes[0].user.username, 'oldnode1-owner')
        self.assertEqual(nodes[1].user.username, 'oldnode2-owner')
        self.assertEqual(nodes[2].user.username, 'oldnode3-pisano')
        self.assertEqual(nodes[3].user.username, 'oldnode4-default')
        self.assertEqual(nodes[4].user.username, 'oldnode1-owner2')
        self.assertEqual(nodes[5].user.username, 'addednode1-owner')
        self.assertEqual(nodes[5].user.email, 'addednode@test.com')
        self.assertEqual(nodes[5].name, 'addednode1')
        self.assertEqual(nodes[5].description, 'addednode1-description')

        device = Device.objects.last()
        self.assertEqual(device.name, 'addeddevice1')

        interface = Interface.objects.last()
        self.assertEqual(interface.name, 'addedeth')
        self.assertEqual(interface.ip_set.count(), 2)

        link = Link.objects.last()
        self.assertEqual(link.interface_b_id, i.id)
        self.assertEqual(link.dbm, -75)

        self.assertEqual(inwards[1].from_name, 'Added')

        # ------ try to cause troubles ------ #

        ot = OldNode(**{
            "name": "troublingnode",
            "slug": "troublingnode",
            "owner": "troublemaker",
            "description": "troublingnode-description",
            "postal_code": "00185",
            "email": "troublemaker@test.com",
            "password": "",
            "lat": 42.4064152946931969,
            "lng": 13.7390629470348003,
            "alt": 23.5,
            "status": "a"
        })
        ot.save()

        troublemaker = User(**{
            "first_name": "Trouble",
            "last_name": "Maker",
            "username": "icausetroubles",
            "email": "troublemaker@test.com"
        })
        troublemaker.save()

        management.call_command('import_old_nodeshot', noinput=True, verbosity=2)

        self.assertEqual(Node.objects.filter(name='troublingnode').count(), 1)
