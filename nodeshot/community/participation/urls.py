from django.conf.urls import patterns, url


urlpatterns = patterns('nodeshot.community.participation.views',  # noqa
    url(r'^nodes/(?P<slug>[-\w]+)/comments/$', 'node_comments', name='api_node_comments'),
    url(r'^nodes/(?P<slug>[-\w]+)/ratings/$', 'node_ratings', name='api_node_ratings'),
    url(r'^nodes/(?P<slug>[-\w]+)/votes/$', 'node_votes', name='api_node_votes'),
)
