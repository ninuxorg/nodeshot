from django.conf.urls import patterns, url


urlpatterns = patterns('nodeshot.ui.open311_demo.views',
    url(r'^$', 'open311', name='open311'),
)