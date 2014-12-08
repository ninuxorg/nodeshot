from django.conf.urls import patterns, url


urlpatterns = patterns('nodeshot.ui.default.views',
    url(r'^$', 'index', name='index'),  # noqa
)
