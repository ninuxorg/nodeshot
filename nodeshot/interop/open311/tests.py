import os
import simplejson as json

from django.core.urlresolvers import reverse
from django.contrib.gis.geos import GEOSGeometry

from nodeshot.core.base.tests import BaseTestCase, user_fixtures

from .serializers import *
from .base import SERVICES


class Open311Request(BaseTestCase):

    fixtures = [
        'initial_data.json',
        user_fixtures,
        'test_layers.json',
        'test_status.json',
        'test_nodes.json',
        'test_images.json'
    ]

    def test_service_discovery(self):
        response = self.client.get(reverse('api_service_discovery'))
        # ensure 4 keys in response
        self.assertEqual(len(response.data), 4)

        # ensure 5 keys for each endpoint
        for endpoint in response.data['endpoints']:
            self.assertEqual(len(endpoint), 5)

    def test_service_list(self):
        response = self.client.get(reverse('api_service_definition_list'))

        # ensure 4 services
        self.assertEqual(len(response.data), 4)

        # ensure these words are in response
        for word in SERVICES.keys():
            self.assertContains(response, word)

    def test_node_service_definition(self):
        response = self.client.get(reverse('api_service_definition_detail', args=['node']))

        # ensure correct service code
        self.assertEqual(response.data['service_code'], 'node')

        # ensure 7 attributes
        self.assertEqual(len(response.data['attributes']), 8)

    def test_vote_service_definition(self):
        response = self.client.get(reverse('api_service_definition_detail', args=['vote']))

        # ensure correct service code
        self.assertEqual(response.data['service_code'], 'vote')

        # ensure 7 attributes
        self.assertEqual(len(response.data['attributes']), 2)

    def test_comment_service_definition(self):
        response = self.client.get(reverse('api_service_definition_detail', args=['comment']))

        # ensure correct service code
        self.assertEqual(response.data['service_code'], 'comment')

        # ensure 7 attributes
        self.assertEqual(len(response.data['attributes']), 2)

    def test_rate_service_definition(self):
        response = self.client.get(reverse('api_service_definition_detail', args=['rate']))

        # ensure correct service code
        self.assertEqual(response.data['service_code'], 'rate')

        # ensure 7 attributes
        self.assertEqual(len(response.data['attributes']), 2)

    def test_service_request_wrong_service(self):
        # check wrong service in service_request
        login = self.client.login(username='admin', password='tester')
        service_request={'service_code':'not_exists'}
        url = "%s" % reverse('api_service_request_list')
        response = self.client.post(url,service_request)
        self.assertEqual(response.status_code, 404)

    def test_service_request_node(self):
        # service_request for nodes
        service_request={
                        'service_code':"node",
                        "name": "montesacro4",
                        "slug": "montesacro4",
                        "layer": "rome",
                        "lat": "22.5253",
                        "long": "41.8890",
                        "description": "test",
                        }
        url = "%s" % reverse('api_service_request_list')
        response = self.client.post(url,service_request)
        # Not authenticated : 403
        self.assertEqual(response.status_code, 403)
        login = self.client.login(username='admin', password='tester')
        # Authenticated users can insert service requests: 201
        response = self.client.post(url,service_request)
        self.assertEqual(response.status_code, 201)

    def test_service_request_node_incomplete_key(self):
        # POST requests

        # incorrect service_request for nodes
        login = self.client.login(username='admin', password='tester')

        service_request={
                        'service_code':"node",
                        "slug": "montesacro4",
                        "layer": "rome",
                        "lat": "22.5253",
                        "long": "41.8890",
                        "description": "test",
                        }
        url = "%s" % reverse('api_service_request_list')
        response = self.client.post(url,service_request)
        self.assertEqual(response.status_code, 400)

    def test_service_request_node_incomplete_value(self):
        # POST requests

        # incorrect service_request for nodes
        login = self.client.login(username='admin', password='tester')

        service_request={
                        'service_code':"node",
                        "name": "",
                        "slug": "montesacro4",
                        "layer": "rome",
                        "lat": "22.5253",
                        "long": "41.8890",
                        "description": "test",
                        }
        url = "%s" % reverse('api_service_request_list')
        response = self.client.post(url,service_request)
        self.assertEqual(response.status_code, 400)

    def test_service_request_vote(self):
        # service_request for votes
        login = self.client.login(username='admin', password='tester')
        service_request={'service_code':"vote","node": 1,"vote":1}
        url = "%s" % reverse('api_service_request_list')
        response = self.client.post(url,service_request)
        self.assertEqual(response.status_code, 201)

    def test_service_request_vote_incomplete(self):
        # incomplete service_request for votes
        login = self.client.login(username='admin', password='tester')
        service_request={'service_code':"vote","vote":1}
        url = "%s" % reverse('api_service_request_list')
        response = self.client.post(url,service_request)

        self.assertEqual(response.status_code, 400)

    def test_service_request_vote_incorrect(self):
        # incorrect service_request for votes
        login = self.client.login(username='admin', password='tester')
        service_request={'service_code':"vote","node": 1,"vote":10}
        url = "%s" % reverse('api_service_request_list')
        response = self.client.post(url,service_request)
        self.assertEqual(response.status_code, 400)

    def test_service_request_rating(self):
        # service_request for rating
        login = self.client.login(username='admin', password='tester')
        service_request={'service_code':"rate","node": 1,"value":1}
        url = "%s" % reverse('api_service_request_list')
        response = self.client.post(url,service_request)

        self.assertEqual(response.status_code, 201)

    def test_service_request_rating_incomplete(self):
        # incomplete service_request for rating
        login = self.client.login(username='admin', password='tester')
        service_request={'service_code':"rate","value":1}
        url = "%s" % reverse('api_service_request_list')
        response = self.client.post(url,service_request)

        self.assertEqual(response.status_code, 400)

    def test_service_request_rating_incorrect(self):
        # incorrect service_request for rating
        login = self.client.login(username='admin', password='tester')
        service_request={'service_code':"rate","node": 1,"value":20}
        url = "%s" % reverse('api_service_request_list')
        response = self.client.post(url,service_request)

        self.assertEqual(response.status_code, 400)

    def test_service_request_comment(self):
        # service_request for comments
        login = self.client.login(username='admin', password='tester')
        service_request={'service_code':"comment","node": 1,"text":"OK"}
        url = "%s" % reverse('api_service_request_list')
        response = self.client.post(url,service_request)

        self.assertEqual(response.status_code, 201)

    def test_service_request_comment_incomplete(self):
        # incomplete service_request for comments
        login = self.client.login(username='admin', password='tester')
        # Vote
        service_request={'service_code':"comment","text":"OK"}
        url = "%s" % reverse('api_service_request_list')
        response = self.client.post(url,service_request)

        self.assertEqual(response.status_code, 400)

    def test_get_service_request(self):
        # GET request detail
        response = self.client.get(reverse('api_service_request_detail', args=['node','1']))
        self.assertEqual(response.status_code, 200)
        # Wrong service code
        response = self.client.get(reverse('api_service_request_detail', args=['wrong','1']))
        self.assertEqual(response.status_code, 404)
        # Not existing request
        response = self.client.get(reverse('api_service_request_detail', args=['node','100']))
        self.assertEqual(response.status_code, 404)

    def test_get_service_requests(self):
        # GET requests list
        response = self.client.get(reverse('api_service_request_list'))
        self.assertEqual(response.status_code, 404)

        parameters = {'service_code': 'node'}
        response = self.client.get(reverse('api_service_request_list'), parameters)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 10)

        parameters['status'] = 'open'
        response = self.client.get(reverse('api_service_request_list'), parameters)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

        parameters['status'] = 'closed'
        response = self.client.get(reverse('api_service_request_list'), parameters)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 7)

        parameters['status'] = 'wrong'
        response = self.client.get(reverse('api_service_request_list'), parameters)
        self.assertEqual(response.status_code, 404)

        # check date parameters
        parameters = {'service_code':'node','start_date':'wrong'}

        response = self.client.get(reverse('api_service_request_list'), parameters)
        self.assertEqual(response.status_code, 404)

        parameters['start_date'] = '2013-01-01T17:57:02Z'
        response = self.client.get(reverse('api_service_request_list'), parameters)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 10)

        parameters['end_date'] = '2013-04-01T17:57:02Z'
        response = self.client.get(reverse('api_service_request_list'), parameters)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        parameters['start_date'] = '2015-01-01T17:57:02Z'
        response = self.client.get(reverse('api_service_request_list'), parameters)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_file_upload(self):
        login = self.client.login(username='admin', password='tester')
        service_request={
                        'service_code':"node",
                        "name": "montesacro4",
                        "slug": "montesacro4",
                        "layer": "rome",
                        "lat": "22.5253",
                        "long": "41.8890",
                        "description": "test",
                        "geometry": "POINT (22.5253334454477372 41.8890404543067518)"
                        }
        with open("%s/templates/image_unit_test.gif" % os.path.dirname(os.path.realpath(__file__)), 'rb') as image_file:
            service_request['file'] = image_file
            url = "%s" % reverse('api_service_request_list')
            response = self.client.post(url,service_request)
            self.assertEqual(response.status_code, 201)

    def test_open311_serializers(self):
        """ ensure serializers can be created this way """
        ServiceRatingSerializer().data
        ServiceCommentSerializer().data
        ServiceNodeSerializer().data
        ServiceVoteSerializer().data
        ServiceListSerializer().data
        NodeRequestSerializer().data
        VoteRequestSerializer().data
        CommentRequestSerializer().data
        RatingRequestSerializer().data
        VoteRequestListSerializer().data
        CommentRequestListSerializer().data
        RatingRequestListSerializer().data
        NodeRequestListSerializer().data
        NodeRequestDetailSerializer().data

    def test_open311_UI(self):
        """ ensure open311 UI can be reached"""
        response = self.client.get(reverse('open311_demo:open311'))
        self.assertEqual(response.status_code, 200)
