from django.conf.urls import patterns, url

urlpatterns = patterns('nodeshot.core.metrics.views',  # noqa
    url(r'^metrics/(?P<pk>[0-9]+)/$', 'metric_details', name='api_metric_details'),
)
