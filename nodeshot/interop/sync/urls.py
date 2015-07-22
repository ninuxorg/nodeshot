from django.conf.urls import patterns, url


urlpatterns = patterns('nodeshot.interop.sync.views',  # noqa
    url(r'^admin/layer-external-reload-schema/(?P<pk>\d+)/$',
        'layer_external_reload_schema',
        name='layer_external_reload_schema'),
)
