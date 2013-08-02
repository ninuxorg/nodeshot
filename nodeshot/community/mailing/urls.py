from django.conf.urls import patterns, url


urlpatterns = patterns('nodeshot.community.mailing.views',
    # contact
    url(r'^/nodes/(?P<slug>[-\w]+)/contact/$', 'contact_node', name='api_node_contact'),
)