from django.conf.urls import patterns, url


urlpatterns = patterns('nodeshot.community.participation.views',  # noqa
    url(r'^layers/(?P<slug>[-\w]+)/comments/$', 'layer_nodes_comments', name='api_layer_nodes_comments'),
    url(r'^layers/(?P<slug>[-\w]+)/participation/$', 'layer_nodes_participation', name='api_layer_nodes_participation'),
    url(r'^comments/$', 'all_nodes_comments', name='api_all_nodes_comments'),
    url(r'^participation/$', 'all_nodes_participation', name='api_all_nodes_participation'),
    url(r'^nodes/(?P<slug>[-\w]+)/comments/$', 'node_comments', name='api_node_comments'),
    url(r'^nodes/(?P<slug>[-\w]+)/ratings/$', 'node_ratings', name='api_node_ratings'),
    url(r'^nodes/(?P<slug>[-\w]+)/votes/$', 'node_votes', name='api_node_votes'),
    url(r'^nodes/(?P<slug>[-\w]+)/participation/$', 'node_participation', name='api_node_participation'),
    url(r'^nodes/(?P<slug>[-\w]+)/participation_settings/$', 'node_participation_settings', name='api_node_participation_settings'),
    url(r'^layers/(?P<slug>[-\w]+)/participation_settings/$', 'layer_participation_settings', name='api_layer_participation_settings'),
)
