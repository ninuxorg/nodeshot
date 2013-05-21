from django.contrib.gis import admin
from django.conf import settings

from nodeshot.core.base.admin import BaseTabularInline

from .models import *


admin.site.register(Rating)
admin.site.register(Comment)
admin.site.register(Vote)


## CUSTOMIZE LAYER ADMIN ##

if 'nodeshot.core.layers' in settings.INSTALLED_APPS:

    if 'nodeshot.interoperability' in settings.INSTALLED_APPS:
        from nodeshot.interoperability.admin import LayerAdmin as BaseLayerAdmin
    else:
        from nodeshot.core.layers.admin import LayerAdmin as BaseLayerAdmin
    
    from nodeshot.core.layers.models import Layer
    
    class LayerSettingsInline(admin.TabularInline):
        model = LayerParticipationSettings
        extra = 1
    
    class LayerAdmin(BaseLayerAdmin):
        inlines = BaseLayerAdmin.inlines + [LayerSettingsInline]
    
    admin.site.unregister(Layer)
    admin.site.register(Layer, LayerAdmin)


## CUSTOMIZE NODE ADMIN ##

from nodeshot.core.nodes.admin import NodeAdmin as BaseNodeAdmin
from nodeshot.core.nodes.models import Node

class NodeSettingsInline(admin.TabularInline):
    model = NodeParticipationSettings
    extra = 1

class CommentInline(BaseTabularInline):
    model = Comment
    extra = 1 
     
class RatingInline(BaseTabularInline):
    model = Rating
    extra = 1 

class VoteInline(BaseTabularInline):
    model = Vote
    extra = 1 

class NodeAdmin(BaseNodeAdmin):
    """ replacement of Node Admin """
    additional_inlindes = [NodeSettingsInline]
    if settings.DEBUG:
        additional_inlindes += [CommentInline, RatingInline, VoteInline]
        
    inlines = BaseNodeAdmin.inlines + additional_inlindes

admin.site.unregister(Node)
admin.site.register(Node, NodeAdmin)
