from django.test import TestCase
from django.contrib.auth.models import AnonymousUser
from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
User = get_user_model()

from nodeshot.core.base.tests import user_fixtures

from ..models import Node, Status, Image


class TestModels(TestCase):
    fixtures = [
        'initial_data.json',
        user_fixtures,
        'test_layers.json',
        'test_status.json',
        'test_nodes.json',
        'test_images.json'
    ]

    def test_status_model(self):
        """ test status model internal mechanism works correctly """
        for status in Status.objects.all():
            status.delete()
        testing = Status(name='testing', slug='testing', description='slug')
        testing.save()
        self.assertEqual(testing.order, 0)
        self.assertEqual(testing.is_default, True)

        active = Status(name='active', slug='active', description='active')
        active.save()
        self.assertEqual(active.order, 1)
        self.assertEqual(active.is_default, False)

        pending = Status(name='pending', slug='pending', description='pending')
        pending.save()
        self.assertEqual(pending.order, 2)
        self.assertEqual(pending.is_default, False)
        pending.is_default = True
        pending.save()
        default_statuses = Status.objects.filter(is_default=True)
        self.assertEqual(default_statuses.count(), 1)
        self.assertEqual(default_statuses[0].pk, pending.pk)

        unconfirmed = Status(name='unconfirmed', slug='unconfirmed', description='unconfirmed', is_default=True)
        unconfirmed.save()
        default_statuses = Status.objects.filter(is_default=True)
        self.assertEqual(default_statuses.count(), 1)
        self.assertEqual(default_statuses[0].pk, unconfirmed.pk)

    def test_current_status(self):
        """ test that node._current_status is none for new nodes """
        n = Node()
        self.failUnlessEqual(n._current_status, None, 'new node _current_status private attribute is different than None')
        n = Node.objects.all().order_by('-id')[0]
        self.failUnlessEqual(n._current_status, n.status.id, 'new node _current_status private attribute is different than status')
        n.status = Status.objects.get(pk=2)
        self.failIfEqual(n._current_status, n.status.id, 'new node _current_status private attribute is still equal to status')
        n.save()
        self.failUnlessEqual(n._current_status, n.status.id, 'new node _current_status private attribute is different than status')
        n.status_id = 3
        n.save()
        n = Node.objects.all().order_by('-id')[0]
        self.failUnlessEqual(n._current_status, n.status.id, 'new node _current_status private attribute is different than status')

    def test_node_manager(self):
        """ test manager methods of Node model """
        # published()
        Node.objects.published
        count = Node.objects.published().filter(layer=1).count()
        # no unplished nodes on that layer, so the count should be the same
        self.assertEqual(count, Node.objects.filter(layer=1).count())
        # unpublish the first
        node = Node.objects.published().filter(layer=1)[0]
        node.is_published = False
        node.save()
        # should be -1
        self.assertEqual(count - 1, Node.objects.published().filter(layer=1).count())

        # Ensure GeoManager distance is available
        pnt = Node.objects.get(slug='pomezia').geometry
        Node.objects.filter(geometry__distance_lte=(pnt, 7000))

        # access level manager
        user = User.objects.get(pk=1, is_superuser=True)
        # superuser can see all nodes
        self.assertEqual(Node.objects.all().count(), Node.objects.accessible_to(user).count())
        # same but passing only user_id
        user_1 = User.objects.get(pk=1)
        self.assertEqual(Node.objects.all().count(), Node.objects.accessible_to(user_1).count())
        # simulate non authenticated user
        self.assertEqual(8, Node.objects.accessible_to(AnonymousUser()).count())
        # public nodes
        self.assertEqual(8, Node.objects.access_level_up_to('public').count())
        # public and registered
        self.assertEqual(9, Node.objects.access_level_up_to('registered').count())
        # public, registered and community
        self.assertEqual(10, Node.objects.access_level_up_to('community').count())

        # --- START CHAINING! WOOOO --- #
        # 9 because we unpublished one
        self.assertEqual(9, Node.objects.published().access_level_up_to('community').count())
        self.assertEqual(9, Node.objects.access_level_up_to('community').published().count())
        # user 1 is admin and can see all the nodes, published() is the same as writing filter(is_published=True)
        count = Node.objects.all().filter(is_published=True).count()
        self.assertEqual(count, Node.objects.published().accessible_to(user_1).count())
        self.assertEqual(count, Node.objects.accessible_to(user_1).published().count())
        # chain with geographic query
        count = Node.objects.all().filter(is_published=True).filter(layer_id=1).count()
        self.assertEqual(count, Node.objects.filter(geometry__distance_lte=(pnt, 70000)).accessible_to(user_1).published().count())
        self.assertEqual(count, Node.objects.accessible_to(user_1).filter(geometry__distance_lte=(pnt, 70000)).published().count())
        self.assertEqual(count, Node.objects.accessible_to(user_1).published().filter(geometry__distance_lte=(pnt, 70000)).count())
        self.assertEqual(count, Node.objects.filter(geometry__distance_lte=(pnt, 70000)).accessible_to(user_1).published().count())

        # slice, first, last, find
        self.assertEqual(Node.objects.last().__class__.__name__, 'Node')
        self.assertEqual(Node.objects.last(), Node.objects.order_by('-id')[0])

        self.assertEqual(Node.objects.first().__class__.__name__, 'Node')
        self.assertEqual(Node.objects.first(), Node.objects.order_by('id')[0])

        self.assertEqual(Node.objects.find(1), Node.objects.get(pk=1))

        self.assertEqual(list(Node.objects.slice('name', 5)), list(Node.objects.order_by('name')[0:5]))
        self.assertEqual(list(Node.objects.slice('-name', 5)), list(Node.objects.order_by('-name')[0:5]))

        # chained
        self.assertEqual(Node.objects.published().first(), Node.objects.filter(is_published=True).order_by('id')[0])
        self.assertEqual(Node.objects.published().last(), Node.objects.filter(is_published=True).order_by('-id')[0])

        self.assertEqual(
            Node.objects.published().access_level_up_to('public').first(),
            Node.objects.filter(is_published=True, access_level__lte=0).order_by('id')[0]
        )
        self.assertEqual(
            Node.objects.published().access_level_up_to('public').last(),
            Node.objects.filter(is_published=True, access_level__lte=0).order_by('-id')[0]
        )

    def test_autogenerate_slug(self):
        n = Node()
        n.name = 'Auto generate this'
        n.layer_id = 1
        n.geometry = 'POINT(12.509303756712 41.881163629853)'
        n.full_clean()
        n.save()
        n.refresh_from_db()
        self.assertEqual(n.slug, 'auto-generate-this')

    def test_node_point(self):
        node = Node.objects.first()
        self.assertEqual(node.point, node.geometry)
        node = Node()
        with self.assertRaises(ValueError):
            node.point
        node.geometry = GEOSGeometry("""{"type": "Polygon", "coordinates": [[[12.501493164066, 41.990441051094], [12.583890625003, 41.957770034531], [12.618222900394, 41.912820024702], [12.607923217778, 41.877552973685], [12.582088180546, 41.82423212474], [12.574148841861, 41.813357913568], [12.551532455447, 41.799730560554], [12.525053688052, 41.795155470656], [12.510505386356, 41.793715689492], [12.43308610535, 41.803249638226], [12.388883300784, 41.813613798573], [12.371030517581, 41.870906276755], [12.382016845706, 41.898511105474], [12.386136718753, 41.912820024702], [12.38064355469, 41.926104006681], [12.38064355469, 41.955727539561], [12.413602539065, 41.974107637675], [12.445188232426, 41.983295698272], [12.45617456055, 41.981254021593], [12.476773925785, 41.985337309484], [12.490506835941, 41.985337309484], [12.506986328129, 41.990441051094], [12.501493164066, 41.990441051094]]]}""")
        node.point  # must not raise GEOSException

    def test_image_manager(self):
        """ test manager methods of Image model """
        # admin can see all the images
        user_1 = User.objects.get(pk=1)
        self.assertEqual(Image.objects.all().count(), Image.objects.accessible_to(user_1).count())

    def test_image_auto_order(self):
        """ test image automatic ordering works correctly """
        # node #3 has already 2 images, therefore the new image auto order should be set to 2
        image = Image(node_id=3, file='test3.jpg')
        image.full_clean()
        image.save()
        self.assertEqual(image.order, 2)

        # node #2 does not have any image, therefore the new image auto order should be set to 0
        image = Image(node_id=2, file='test2.jpg')
        image.full_clean()
        image.save()
        self.assertEqual(image.order, 0)

    def test_geometry_collection_with_single_item(self):
        node = Node.objects.get(pk=1)
        node.geometry = GEOSGeometry("GEOMETRYCOLLECTION(POINT(12.509303756712 41.881163629853))")
        node.save()
        # fetch again cos geometry value is modified while saving
        node = Node.objects.get(pk=1)
        point = GEOSGeometry("POINT(12.509303756712 41.881163629853)")
        self.assertEqual(node.geometry, point)

    def test_node_integrity_error_model(self):
        node = Node(**{
            "name": "pomezia",
            "slug": "",
            "layer_id": 1,
            "geometry": 'POINT (12.50094473361969 41.66767450196442)',
            "elev": 0,
            "address": "",
            "description": ""
        })
        with self.assertRaises(ValidationError):
            node.full_clean()

    def test_slug_changes_automatically(self):
        # change name 0
        existing = Node.objects.get(slug='pomezia')
        existing.name = 'Changed'
        existing.full_clean()
        existing.save()
        # query again to be sure data is up to date
        existing = Node.objects.get(pk=existing.pk)
        self.assertEqual(existing.slug, 'changed')
