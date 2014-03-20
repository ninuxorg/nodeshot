from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

from nodeshot.core.nodes.models import Node, Status, Image
from nodeshot.core.layers.models import Layer
from nodeshot.community.participation.models import Vote, Comment, Rating
from nodeshot.community.participation.models import LayerParticipationSettings, NodeParticipationSettings
from nodeshot.community.participation.models import NodeRatingCount


def map_view(request):

    return render(request,'interface/index.html')


