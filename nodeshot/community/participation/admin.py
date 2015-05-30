from django.contrib.gis import admin
from django.conf import settings

from nodeshot.core.base.admin import BaseTabularInline

from .models import Comment, Vote, Rating, NodeParticipationSettings


admin.site.register(Rating)
admin.site.register(Comment)
admin.site.register(Vote)


# ------ EXTEND LAYER ADMIN ------ #

if 'nodeshot.core.layers' in settings.INSTALLED_APPS:

    from nodeshot.core.layers.admin import LayerAdmin
    from .models import LayerParticipationSettings

    class LayerSettingsInline(admin.TabularInline):
        model = LayerParticipationSettings
        extra = 1

    LayerAdmin.inlines.append(LayerSettingsInline)


# ------ EXTEND NODE ADMIN ------ #

from nodeshot.core.nodes.admin import NodeAdmin


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


additional_inlines = [NodeSettingsInline]

if settings.DEBUG:
    additional_inlines += [CommentInline, RatingInline, VoteInline]

NodeAdmin.inlines = NodeAdmin.inlines + additional_inlines
