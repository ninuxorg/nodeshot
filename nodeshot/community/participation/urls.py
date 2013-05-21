from django.conf.urls import patterns, include, url
from rest_framework.urlpatterns import format_suffix_patterns


from nodeshot.community.participation import views


urlpatterns = patterns('nodeshot.core.nodes.views',
    url(r'^/comments/$', views.CommentAdd.as_view()),
    url(r'^/comments/(?P<pk>[0-9]+)/$', views.CommentDetail.as_view()),
    url(r'^/votes/$', views.VoteAdd.as_view()),
    url(r'^/ratings/$', views.RatingAdd.as_view()),
    url(r'nodes/comments/$', views.NodeCommentList.as_view()),
    url(r'nodes/participation/$', views.NodeParticipationList.as_view()),
    url(r'nodes/(?P<slug>[-\w]+)/comments/$', views.NodeCommentDetail.as_view()),
    url(r'nodes/(?P<slug>[-\w]+)/participation/$', views.NodeParticipationDetail.as_view()),
)

urlpatterns = format_suffix_patterns(urlpatterns)