"""
Unit tests for participation app
"""
from django.contrib.auth.models import User
from django.test import TestCase
from django.core.urlresolvers import reverse

from nodeshot.core.nodes.models import Node
from .models import Comment, Rating, Vote


class ParticipationModelsTest(TestCase):
    """ Models tests """
    
    fixtures = [
        'initial_data.json',
        'test_users.json',
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
        
    def test_comments_api(self,*args,**kwargs):
        """
        Comments endpoint should be reachable with GET and return 404 if object is not found.
        POST method allowed
        """
        node = Node.objects.get(pk=1)
        node_slug=node.slug
        fake_node_slug="nonesisto"
        
        # api_node_comments
        
        # GET
        
        response = self.client.get(reverse('api_node_comments',args=[node_slug]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('api_node_comments',args=[fake_node_slug]))
        self.assertEqual(response.status_code, 404)
        
        #POST
        
        #FIXME: non riesco ad accedere alla URL se non esplicitamente-
        #Tutti i seguenti metodi non funzionano:
        #Metodo 1
        #response = self.client.post(reverse('api_node_comments',kwargs={'slug':'fusolab','node': '1', 'text': 'test_comment', 'user': '2'}))
        #Metodo 2
        #url="/api/v1/nodes/%s/comments/ " % (node_slug)
        #response = self.client.post(url,post_data)
        
        login=self.client.login(username='admin', password='tester')
        good_post_data= {"node": 1, "text": "test_comment", "user": 2}
        bad_post_data= {"node": 100, "text": "test_comment", "user": 2}
        
        #wrong slug -- 404
        response = self.client.post('/api/v1/nodes/notexists/comments/',good_post_data)
        self.assertEqual(response.status_code, 404)
        
        #wrong POST data -- 400
        response = self.client.post('/api/v1/nodes/fusolab/comments/',bad_post_data)
        self.assertEqual(response.status_code, 400)
        
        #Correct  POST data and correct slug-- 201
        response = self.client.post('/api/v1/nodes/fusolab/comments/',good_post_data)
        self.assertEqual(response.status_code, 201)
        
        #User not allowed -- 403
        self.client.logout()
        response = self.client.post('/api/v1/nodes/fusolab/comments/',good_post_data)
        self.assertEqual(response.status_code, 403)
        
    def test_participation_api(self,*args,**kwargs):
        """
        Participation endpoint should be reachable only with GET and return 404 if object is not found.
        """
        node = Node.objects.get(pk=1)
        node_slug=node.slug
        fake_node_slug="nonesisto"
        
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
        fake_node_slug="nonesisto"
        
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
        Ratings endpoint should be reachable only with POST and return 404 if object is not found.
        """
        node = Node.objects.get(pk=1)
        node_slug=node.slug
        fake_node_slug="nonesisto"
        
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