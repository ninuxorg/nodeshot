from django.conf.urls import patterns, url


urlpatterns = patterns('nodeshot.ui.default.api.views',
    url(r'^ui/essential_data.json$', 'essential_data', name='api_ui_essential_data'),
)
