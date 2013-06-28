"""
Unit tests for participation app
"""
from django.contrib.auth import get_user_model
User = get_user_model()
from django.test import TestCase
from django.core.urlresolvers import reverse

import simplejson as json

from nodeshot.core.nodes.models import Node
from nodeshot.core.layers.models import Layer
from nodeshot.core.base.tests import user_fixtures

from .models import Comment, Rating, Vote


class ParticipationModelsTest(TestCase):
    """ Models tests """
    
    fixtures = [
        'initial_data.json',
        user_fixtures,
        'test_layers.json',
        'test_nodes.json',
        'test_images.json'
    ]
    
    def test_added_methods(self):
        node = Node.objects.get(pk=1)
        # ensure noderatingcount related object is automatically created with signals
        #node.noderatingcount
        node.rating_count
        node.participation_settings
        node.layer.participation_settings
    
    def test_update_comment_count(self):
        """
        Comment count should be updated when a comment is created or deleted
        """
        # ensure comment count is 0
        node = Node.objects.get(pk=1)
        self.assertEqual(0, node.rating_count.comment_count)
        # create a new comment
        comment = Comment(node_id=1, user_id=1, text='test comment')
        comment.save()
        # now should have incremented by 1
        node = Node.objects.get(pk=1)
        self.assertEqual(1, node.rating_count.comment_count)
        
        # delete comment and ensure the count gets back to 0
        comment.delete()
        node = Node.objects.get(pk=1)
        self.assertEqual(0, node.rating_count.comment_count)
    
    def test_update_rating_count(self):
        """
        Rating count and average should be updated when a rating is created or deleted
        """
        # ensure rating count is 0
        node = Node.objects.get(pk=1)
        self.assertEqual(0, node.rating_count.rating_count)
        self.assertEqual(0, node.rating_count.rating_avg)
        # create a new rating
        rating = Rating(node_id=1, user_id=1, value=10)
        rating.save()
        # now should have incremented by 1 and average should be 10
        node = Node.objects.get(pk=1)
        self.assertEqual(1, node.rating_count.rating_count)
        self.assertEqual(10, node.rating_count.rating_avg)
        
        # delete rating and ensure the counts get back to 0
        rating.delete()
        node = Node.objects.get(pk=1)
        self.assertEqual(0, node.rating_count.rating_count)
        self.assertEqual(0, node.rating_count.rating_avg)
    
    def test_update_vote_count(self):
        """
        Likes and dislikes count should be updated when a vote is created or deleted
        """
        # ensure likes and dislikes count are 0
        node = Node.objects.get(pk=1)
        self.assertEqual(0, node.rating_count.likes)
        self.assertEqual(0, node.rating_count.dislikes)
        # create a new like
        like = Vote(node_id=1, user_id=1, vote=1)
        like.save()
        # likes should have incremented by 1
        node = Node.objects.get(pk=1)
        self.assertEqual(1, node.rating_count.likes)
        self.assertEqual(0, node.rating_count.dislikes)
        # create a new dislike
        dislike = Vote(node_id=1, user_id=2, vote=-1)
        dislike.save()
        # dislikes should have incremented by 1
        node = Node.objects.get(pk=1)
        self.assertEqual(1, node.rating_count.likes)
        self.assertEqual(1, node.rating_count.dislikes)
        
        # delete like and count should get back to 0
        like.delete()
        node = Node.objects.get(pk=1)
        self.assertEqual(0, node.rating_count.likes)
        self.assertEqual(1, node.rating_count.dislikes)
        
        # delete dislike and count should get back to 0
        dislike.delete()
        node = Node.objects.get(pk=1)
        self.assertEqual(0, node.rating_count.likes)
        self.assertEqual(0, node.rating_count.dislikes)
        
    def test_node_comment_api(self,*args,**kwargs):
        """
        Comments endpoint should be reachable with GET and return 404 if object is not found.
        POST method allowed
        """
        node = Node.objects.get(pk=1)
        node_slug = node.slug
        node_id=node.id
        node2 = Node.objects.get(pk=2)
        node2_slug = node2.slug
        fake_node_slug = "idontexist"
        layer = Layer.objects.get(pk=node.layer_id)
        
        url = reverse('api_node_comments', args=[node_slug])
        url2 = reverse('api_node_comments', args=[node2_slug])
        wrong_url = reverse('api_node_comments', args=[fake_node_slug])
        
        # api_node_comments
        
        # GET
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(wrong_url)
        self.assertEqual(response.status_code, 404)       
        
        #POST
        
        login = self.client.login(username='admin', password='tester')
        good_post_data = {"text": "test_comment"}
        bad_post_data = {"node": 100, "text": "test_comment", "user": 2}
        
        #wrong slug -- 404
        response = self.client.post(wrong_url,good_post_data)
        self.assertEqual(response.status_code, 404)
        
        # correct POST data and correct slug -- 201
        response = self.client.post(url, good_post_data)
        self.assertEqual(response.status_code, 201)
        
        # POSTing a comment for node2
        response = self.client.post(url2, good_post_data)
        self.assertEqual(response.status_code, 201)
        
        #GET should not return both the comments inserted above     
        response = self.client.get(url)
        comments = json.loads(response.content)
        node_comments_count = Comment.objects.filter(node_id=node_id).count()
        self.assertEqual(node_comments_count, len(comments))
        
        #Comments not allowed on layer
        node.layer.participation_settings.comments_allowed = False
        node.layer.participation_settings.save()
        response = self.client.post(url, good_post_data)
        self.assertEqual(response.status_code, 400)
        node.layer.participation_settings.comments_allowed = True
        node.layer.participation_settings.save()
        response = self.client.post(url, good_post_data)
        self.assertEqual(response.status_code, 201)
        
        #Comments not allowed on node
        node.participation_settings.comments_allowed = False
        node.participation_settings.save()
        response = self.client.post(url, good_post_data)
        self.assertEqual(response.status_code, 400)
        node.participation_settings.comments_allowed = True
        node.participation_settings.save()
        response = self.client.post(url, good_post_data)
        self.assertEqual(response.status_code, 201)
        
        # User not allowed -- 403
        self.client.logout()
        response = self.client.post(url, good_post_data)
        self.assertEqual(response.status_code, 403)
               
    def test_node_participation_api(self,*args,**kwargs):
        """
        Participation endpoint should be reachable only with GET and return 404 if object is not found.
        """
        node = Node.objects.get(pk=1)
        node_slug=node.slug
        fake_node_slug="idontexist"
        
        # api_node_participation
        
        # GET
        
        response = self.client.get(reverse('api_node_participation',args=[node_slug]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('api_node_participation',args=[fake_node_slug]))
        self.assertEqual(response.status_code, 404)
        
        # POST not allowed -- 405
        
        #FIXME: non riesco ad accedere alla URL se non esplicitamente-
        
        login=self.client.login(username='admin', password='tester')
        response = self.client.post('/api/v1/nodes/fusolab/participation/',args=[node_slug])
        self.assertEqual(response.status_code, 405)
    
    def test_ratings_api(self,*args,**kwargs):    
        """
        Ratings endpoint should be reachable only with POST and return 404 if object is not found.
        """
        node = Node.objects.get(pk=1)
        node_slug=node.slug
        fake_node_slug="idontexist"
        
        # api_node_ratings
        
        # GET not allowed -- 405
        
        response = self.client.get(reverse('api_node_ratings',args=[node_slug]))
        self.assertEqual(response.status_code, 405)
        
        #POST
        
        #FIXME: non riesco ad accedere alla URL se non esplicitamente-
        
        login=self.client.login(username='admin', password='tester')
        good_post_data= {"node": 1, "value": "5", "user": 2}
        
        #wrong slug -- 404
        response = self.client.post('/api/v1/nodes/notexists/ratings/',good_post_data)
        self.assertEqual(response.status_code, 404)
        
        #wrong POST data (node not exists ) -- 400
        bad_post_data= {"node": 100, "value": "5", "user": 2}
        response = self.client.post('/api/v1/nodes/fusolab/ratings/',bad_post_data)
        self.assertEqual(response.status_code, 400)
        
        #wrong POST data (wrong rating) -- 400
        bad_post_data= {"node": 1, "value": "12", "user": 2}
        response = self.client.post('/api/v1/nodes/fusolab/ratings/',bad_post_data)
        self.assertEqual(response.status_code, 400)
        
        #Correct  POST data and correct slug-- 201
        response = self.client.post('/api/v1/nodes/fusolab/ratings/',good_post_data)
        self.assertEqual(response.status_code, 201)
        
        #User not allowed -- 403
        self.client.logout()
        response = self.client.post('/api/v1/nodes/fusolab/ratings/',good_post_data)
        self.assertEqual(response.status_code, 403)
        
    def test_votes_api(self,*args,**kwargs):    
        """
        Vote endpoint should be reachable only with POST and return 404 if object is not found.
        """
        node = Node.objects.get(pk=1)
        node_slug=node.slug
        fake_node_slug="idontexist"
        
        # api_node_ratings
        
        # GET not allowed -- 405
        
        response = self.client.get(reverse('api_node_votes',args=[node_slug]))
        self.assertEqual(response.status_code, 405)
        
        #POST
        
        #FIXME: non riesco ad accedere alla URL se non esplicitamente-
        
        login=self.client.login(username='admin', password='tester')
        good_post_data= {"node": 1, "vote": "1", "user": 2}
        
        #wrong slug -- 404
        response = self.client.post('/api/v1/nodes/notexists/votes/',good_post_data)
        self.assertEqual(response.status_code, 404)
        
        #wrong POST data (node not exists ) -- 400
        bad_post_data= {"node": 100, "vote": "1", "user": 2}
        response = self.client.post('/api/v1/nodes/fusolab/votes/',bad_post_data)
        self.assertEqual(response.status_code, 400)
        
        #wrong POST data (wrong vote) -- 400
        bad_post_data= {"node": 1, "vote": "3", "user": 2}
        response = self.client.post('/api/v1/nodes/fusolab/votes/',bad_post_data)
        self.assertEqual(response.status_code, 400)
        
        #Correct  POST data and correct slug-- 201
        response = self.client.post('/api/v1/nodes/fusolab/votes/',good_post_data)
        self.assertEqual(response.status_code, 201)
        
        #User not allowed -- 403
        self.client.logout()
        response = self.client.post('/api/v1/nodes/fusolab/votes/',good_post_data)
        self.assertEqual(response.status_code, 403)
        
    def test_layer_comments_api(self, *args,**kwargs):
        """
        Layer comments endpoint should be reachable only with GET and return 404 if object is not found.
        """
        layer = Layer.objects.get(pk=1)
        layer_slug=layer.slug
        fake_layer_slug="idontexist"
        
        # api_layer_nodes_comments
        
        # GET
        
        response = self.client.get(reverse('api_layer_nodes_comments',args=[layer_slug]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('api_layer_nodes_comments',args=[fake_layer_slug]))
        self.assertEqual(response.status_code, 404)
        
    def test_layer_participation_api(self, *args,**kwargs):
        """
        Layer participation endpoint should be reachable only with GET and return 404 if object is not found.
        """
        layer = Layer.objects.get(pk=1)
        layer_slug=layer.slug
        fake_layer_slug="idontexist"
        
        # api_layer_nodes_participation
        
        # GET
        
        response = self.client.get(reverse('api_layer_nodes_participation',args=[layer_slug]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('api_layer_nodes_participation',args=[fake_layer_slug]))
        self.assertEqual(response.status_code, 404)
            
    