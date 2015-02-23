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


class ParticipationTests(TestCase):
    """ Models tests """

    fixtures = [
        'initial_data.json',
        user_fixtures,
        'test_layers.json',
        'test_status.json',
        'test_nodes.json',
        'test_images.json'
    ]

    def test_added_methods(self):
        node = Node.objects.get(pk=1)
        # ensure noderatingcount related object is automatically created with signals
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

    def test_rating_model(self):
        self.assertEqual(Rating.objects.count(), 0)
        user = User.objects.first()
        node = Node.objects.first()
        r = Rating(user=user, node=node, value=5)
        r.full_clean()
        r.save()
        self.assertEqual(Rating.objects.count(), 1)
        self.assertEqual(Rating.objects.last().value, 5)

        r = Rating(user=user, node=node, value=2)
        r.full_clean()
        r.save()
        self.assertEqual(Rating.objects.count(), 1)
        self.assertEqual(Rating.objects.last().value, 2)

    def test_node_comment_api(self):
        """
        Comments endpoint should be reachable with GET and return 404 if object is not found.
        POST method allowed
        """
        node = Node.objects.get(pk=1)
        node_slug = node.slug
        node_id = node.id
        node2 = Node.objects.get(pk=2)
        node2_slug = node2.slug
        fake_node_slug = "idontexist"

        url = reverse('api_node_comments', args=[node_slug])
        url2 = reverse('api_node_comments', args=[node2_slug])
        wrong_url = reverse('api_node_comments', args=[fake_node_slug])

        # api_node_comments

        # GET

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # add two comments to two different nodes for testing purposes
        Comment.objects.create(node=node, user_id=1, text='node 1, user 1')
        Comment.objects.create(node=node2, user_id=2, text='node 2, user 2')

        # ensure the right amounts of comments are loaded!
        response = self.client.get(url)
        self.assertEqual(len(json.loads(response.content)), Comment.objects.filter(node=node).count())

        response = self.client.get(wrong_url)
        self.assertEqual(response.status_code, 404)

        # POST
        self.client.login(username='admin', password='tester')
        good_post_data = {"text": "test_comment"}
        bad_post_data = {"node": 100, "text": "test_comment_bad", "user": 2}

        # wrong slug -- 404
        response = self.client.post(wrong_url, good_post_data)
        self.assertEqual(response.status_code, 404)

        # correct POST data and correct slug -- 201
        response = self.client.post(url, good_post_data)
        self.assertEqual(response.status_code, 201)

        # POST 201 - ensure additional post data "user" and "node" are ignored
        response = self.client.post(url, bad_post_data)
        self.assertEqual(response.status_code, 201)
        comment_dict = json.loads(response.content)
        self.assertEqual(comment_dict['user'], 1)
        self.assertEqual(comment_dict['node'], 1)
        self.assertEqual(comment_dict['text'], "test_comment_bad")

        # POSTing a comment for node2
        response = self.client.post(url2, good_post_data)
        self.assertEqual(response.status_code, 201)

        # GET should not return both the comments inserted above
        response = self.client.get(url)
        comments = json.loads(response.content)
        node_comments_count = Comment.objects.filter(node_id=node_id).count()
        self.assertEqual(node_comments_count, len(comments))

        # Comments not allowed on layer
        node.layer.participation_settings.comments_allowed = False
        node.layer.participation_settings.save()
        response = self.client.post(url, good_post_data)
        self.assertEqual(response.status_code, 400)
        node.layer.participation_settings.comments_allowed = True
        node.layer.participation_settings.save()
        response = self.client.post(url, good_post_data)
        self.assertEqual(response.status_code, 201)

        # Comments not allowed on node
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

    def test_ratings_api(self):
        """
        Ratings endpoint should be reachable only with POST and return 404 if object is not found.
        """
        node = Node.objects.get(pk=1)
        node_slug = node.slug
        fake_node_slug = "idontexist"

        url = reverse('api_node_ratings', args=[node_slug])
        wrong_url = reverse('api_node_ratings', args=[fake_node_slug])

        # api_node_ratings

        # GET not allowed -- 405

        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

        # POST
        self.client.login(username='admin', password='tester')
        good_post_data = {"value": "5"}

        # wrong slug -- 404
        response = self.client.post(wrong_url, good_post_data)
        self.assertEqual(response.status_code, 404)

        # wrong POST data (wrong rating) -- 400
        bad_post_data = {"node": 1, "value": "12", "user": 2}
        response = self.client.post(url, bad_post_data)
        self.assertEqual(response.status_code, 400)

        # Correct  POST data and correct slug-- 201
        response = self.client.post(url, good_post_data)
        self.assertEqual(response.status_code, 201)

        # POST 201
        response = self.client.post(url, good_post_data)
        self.assertEqual(response.status_code, 201)

        # POST 201 - ensure additional post data "user" and "node" are ignored
        # Tested as a different user or 400 would be returned because 'value' and 'user' are unique_together
        self.client.login(username='romano', password='tester')
        bad_post_data = {"node": 100, "value": "10", "user": 2}
        response = self.client.post(url, bad_post_data)
        self.assertEqual(response.status_code, 201)
        ratings_dict = json.loads(response.content)
        self.assertEqual(ratings_dict['user'], 4)
        self.assertEqual(ratings_dict['node'], 1)
        self.assertEqual(ratings_dict['value'], 10)

        # Rating not allowed on layer
        # Tested as a different user or 400 would be returned because 'value' and 'user' are unique_together
        self.client.logout()
        self.client.login(username='pisano', password='tester')
        node.layer.participation_settings.rating_allowed = False
        node.layer.participation_settings.save()
        response = self.client.post(url, good_post_data)
        self.assertEqual(response.status_code, 400)
        node.layer.participation_settings.rating_allowed = True
        node.layer.participation_settings.save()
        response = self.client.post(url, good_post_data)
        self.assertEqual(response.status_code, 201)

        # Rating not allowed on node
        # Tested as a different user or 400 would be returned because 'value' and 'user' are unique_together
        self.client.logout()
        self.client.login(username='viterbese', password='tester')
        node.participation_settings.rating_allowed = False
        node.participation_settings.save()
        response = self.client.post(url, good_post_data)
        self.assertEqual(response.status_code, 400)
        node.participation_settings.rating_allowed = True
        node.participation_settings.save()
        response = self.client.post(url, good_post_data)
        self.assertEqual(response.status_code, 201)

        # User not allowed -- 403
        self.client.logout()
        response = self.client.post(url, good_post_data)
        self.assertEqual(response.status_code, 403)

    def test_votes_api(self):
        """
        Vote endpoint should be reachable only with POST and return 404 if object is not found.
        """
        node = Node.objects.get(pk=1)
        node_slug = node.slug
        fake_node_slug = "idontexist"
        url = reverse('api_node_votes', args=[node_slug])
        wrong_url = reverse('api_node_votes', args=[fake_node_slug])
        # GET not allowed -- 405
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        self.client.login(username='admin', password='tester')
        good_post_data = {"vote": "1"}
        # wrong slug -- 404
        response = self.client.post(wrong_url, good_post_data)
        self.assertEqual(response.status_code, 404)
        # wrong POST data (wrong vote) -- 400
        bad_post_data = {"vote": "3"}
        response = self.client.post(url, bad_post_data)
        self.assertEqual(response.status_code, 400)
        # Correct  POST data and correct slug -- 201
        response = self.client.post(url, good_post_data)
        self.assertEqual(response.status_code, 201)
        # same result as before even if trying to change node and user
        response = self.client.post(reverse('api_node_votes', args=['pomezia']), {"node": 100, "vote": "1", "user": 3})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Vote.objects.filter(node__slug='pomezia', user__username='admin').count(), 1)
        self.assertEqual(Vote.objects.filter(node__slug='pomezia', user__username='admin').first().vote, 1)

    def test_votes_api_delete_ok(self):
        self.client.login(username='admin', password='tester')
        url = reverse('api_node_votes', args=['pomezia'])
        # CREATE
        response = self.client.post(url, {"vote": "1"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Vote.objects.filter(node__slug='pomezia', user__username='admin').count(), 1)
        self.assertEqual(Vote.objects.filter(node__slug='pomezia', user__username='admin').first().vote, 1)
        # DELETE
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Vote.objects.filter(node__slug='pomezia', user__username='admin').count(), 0)

    def test_votes_api_delete_fail(self):
        self.client.login(username='admin', password='tester')
        url = reverse('api_node_votes', args=['pomezia'])
        # DELETE FAILS
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 400)

    def test_votes_api_new_vote_changes_old_one(self):
        self.client.login(username='admin', password='tester')
        url = reverse('api_node_votes', args=['pomezia'])
        # 201
        response = self.client.post(url, {"vote": "1"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Vote.objects.filter(node__slug='pomezia', user__username='admin').count(), 1)
        self.assertEqual(Vote.objects.filter(node__slug='pomezia', user__username='admin').first().vote, 1)
        # POST 201 - repeating the same vote deletes old vote
        response = self.client.post(url, {"vote": "-1"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Vote.objects.filter(node__slug='pomezia', user__username='admin').count(), 1)
        self.assertEqual(Vote.objects.filter(node__slug='pomezia', user__username='admin').first().vote, -1)

    def test_votes_api_post(self):
        # POST 201 - ensure additional post data "user" and "node" are ignored
        self.client.login(username='admin', password='tester')
        response = self.client.post(reverse('api_node_votes', args=['eigenlab']), {"vote": "1"})
        self.assertEqual(response.status_code, 201)
        votes_dict = json.loads(response.content)
        self.assertEqual(votes_dict['user'], 1)
        self.assertEqual(votes_dict['node'], 2)
        self.assertEqual(votes_dict['vote'], 1)

    def test_votes_api_not_allowed_on_layer(self):
        self.client.login(username='admin', password='tester')
        url = reverse('api_node_votes', args=['tulug'])
        node = Node.objects.get(slug='tulug')
        # Voting not allowed on layer
        node.layer.participation_settings.voting_allowed = False
        node.layer.participation_settings.save()
        response = self.client.post(url, {"vote": "1"})
        self.assertEqual(response.status_code, 400)
        node.layer.participation_settings.voting_allowed = True
        node.layer.participation_settings.save()
        response = self.client.post(url, {"vote": "1"})
        self.assertEqual(response.status_code, 201)

    def test_votes_api_not_allowed_on_node(self):
        self.client.login(username='admin', password='tester')
        url = reverse('api_node_votes', args=['tulug'])
        node = Node.objects.get(slug='tulug')
        # Voting not allowed on node
        node.participation_settings.voting_allowed = False
        node.participation_settings.save()
        response = self.client.post(url, {"vote": "1"})
        self.assertEqual(response.status_code, 400)
        node.participation_settings.voting_allowed = True
        node.participation_settings.save()
        response = self.client.post(url, {"vote": "1"})
        self.assertEqual(response.status_code, 201)

    def test_votes_api_post_not_allowed_by_user(self):
        # User not allowed -- 403
        response = self.client.post(reverse('api_node_votes', args=['tulug']), {"vote": "1"})
        self.assertEqual(response.status_code, 403)

    def test_layer_comments_api(self):
        """
        Layer comments endpoint should be reachable only with GET and return 404 if object is not found.
        """
        layer = Layer.objects.get(pk=1)
        layer_slug = layer.slug
        fake_layer_slug = "idontexist"
        url = reverse('api_layer_nodes_comments', args=[layer_slug])
        wrong_url = reverse('api_layer_nodes_comments', args=[fake_layer_slug])

        # api_layer_nodes_comments

        # GET
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(wrong_url)
        self.assertEqual(response.status_code, 404)

        # POST not allowed -- 405
        self.client.login(username='admin', password='tester')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 405)

    def test_layer_participation_api(self):
        """
        Layer participation endpoint should be reachable only with GET and return 404 if object is not found.
        """
        layer = Layer.objects.get(pk=1)
        layer_slug = layer.slug
        fake_layer_slug = "idontexist"
        url = reverse('api_layer_nodes_participation', args=[layer_slug])
        wrong_url = reverse('api_layer_nodes_participation', args=[fake_layer_slug])

        # api_layer_nodes_participation

        # GET
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(wrong_url)
        self.assertEqual(response.status_code, 404)

        # POST not allowed -- 405
        self.client.login(username='admin', password='tester')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 405)

    def test_node_participation_api(self):
        """
        Participation endpoint should be reachable only with GET and return 404 if object is not found.
        """
        node = Node.objects.get(pk=1)
        node_slug = node.slug
        fake_node_slug = "idontexist"
        url = reverse('api_node_participation', args=[node_slug])
        wrong_url = reverse('api_node_participation', args=[fake_node_slug])

        # api_node_participation

        # GET
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        participation_dict = json.loads(response.content)
        likes_count = node.noderatingcount.likes
        dislikes_count = node.noderatingcount.dislikes
        comment_count = node.noderatingcount.comment_count
        rating_count = node.noderatingcount.rating_count
        rating_avg = node.noderatingcount.rating_avg
        self.assertEqual(participation_dict['participation']['likes'], likes_count)
        self.assertEqual(participation_dict['participation']['dislikes'], dislikes_count)
        self.assertEqual(participation_dict['participation']['comment_count'], comment_count)
        self.assertEqual(participation_dict['participation']['rating_count'], rating_count)
        self.assertEqual(participation_dict['participation']['rating_avg'], rating_avg)
        response = self.client.get(wrong_url)
        self.assertEqual(response.status_code, 404)

        # POST not allowed -- 405
        self.client.login(username='admin', password='tester')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 405)

    def test_voted_on_node(self):
        node = Node.objects.get(pk=1)
        url = reverse('api_node_details', args=[node.slug])

        # logged out expects False
        self.client.logout()
        response = self.client.get(url)
        self.assertEqual(response.data['relationships']['voted'], False)

        # logged in not voted yet expects False
        self.client.login(username='admin', password='tester')
        response = self.client.get(url)
        self.assertEqual(response.data['relationships']['voted'], False)

        # has already liked expects 1
        v = Vote.objects.create(node_id=node.id, user_id=1, vote=1)
        response = self.client.get(url)
        self.assertEqual(response.data['relationships']['voted'], 1)

        # has already disliked expects -1
        v.delete()
        v = Vote.objects.create(node_id=node.id, user_id=1, vote=-1)
        response = self.client.get(url)
        self.assertEqual(response.data['relationships']['voted'], -1)

    def test_voting_allowed(self):
        node = Node.objects.last()
        self.assertTrue(node.voting_allowed)
        # disable voting on layer
        node.layer.participation_settings.voting_allowed = False
        node.layer.participation_settings.save()
        self.assertFalse(node.voting_allowed)
        # re-enable on layer
        node.layer.participation_settings.voting_allowed = True
        node.layer.participation_settings.save()
        self.assertTrue(node.voting_allowed)
        # disable on node
        node.participation_settings.voting_allowed = False
        node.participation_settings.save()
        self.assertFalse(node.voting_allowed)

    def test_rating_allowed(self):
        node = Node.objects.last()
        self.assertTrue(node.rating_allowed)
        # disable rating on layer
        node.layer.participation_settings.rating_allowed = False
        node.layer.participation_settings.save()
        self.assertFalse(node.rating_allowed)
        # re-enable on layer
        node.layer.participation_settings.rating_allowed = True
        node.layer.participation_settings.save()
        self.assertTrue(node.rating_allowed)
        # disable on node
        node.participation_settings.rating_allowed = False
        node.participation_settings.save()
        self.assertFalse(node.rating_allowed)

    def test_comments_allowed(self):
        node = Node.objects.last()
        self.assertTrue(node.comments_allowed)
        # disable comments on layer
        node.layer.participation_settings.comments_allowed = False
        node.layer.participation_settings.save()
        self.assertFalse(node.comments_allowed)
        # re-enable on layer
        node.layer.participation_settings.comments_allowed = True
        node.layer.participation_settings.save()
        self.assertTrue(node.comments_allowed)
        # disable on node
        node.participation_settings.comments_allowed = False
        node.participation_settings.save()
        self.assertFalse(node.comments_allowed)
