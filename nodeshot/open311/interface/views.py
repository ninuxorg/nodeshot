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
    #if 'nodeshot.community.participation' in settings.INSTALLED_APPS:
    #    context = {'participation': True}
    #else:
    #    context = {'participation': False}
    return render(request,'interface/index.html')

def request_view(request,*args,**kwargs):
    request_id = kwargs['request_id']
    node_id = int(request_id.split("-")[1])
    node = Node.objects.get(pk=node_id)
    layer = node.layer
    layer_name = layer.name
       
    
    layer_comments = layer.layer_participation_settings.comments_allowed
    layer_voting = layer.layer_participation_settings.voting_allowed
    layer_rating = layer.layer_participation_settings.rating_allowed
    
    node_comments = node.node_participation_settings.comments_allowed
    node_voting = node.node_participation_settings.voting_allowed
    node_rating = node.node_participation_settings.rating_allowed
    
    if layer_comments is True  and node_comments is True :
        comments = node.noderatingcount.comment_count
    else:
        comments = "Not allowed for this node"
        
    if layer_voting is True  and node_voting is True :
        likes = node.noderatingcount.likes
        dislikes = node.noderatingcount.dislikes
    else:
        likes = "Not allowed for this node"
        dislikes = "Not allowed for this node"
        
    if layer_rating is True  and node_rating is True :
        rating_avg = node.noderatingcount.rating_avg
        rating_count = node.noderatingcount.rating_count
    else:
        rating_avg = "Not allowed for this node"
        rating_count = "Not allowed for this node"
           
    context = {'request_id':request_id,
               #'participation': True,
               'layer' : layer,
               'node': node,
               'comments': comments,
               'likes': likes,
               'dislikes': dislikes,
               'rating_avg': rating_avg,
               'rating_count': rating_count
               }

    return render(request,'interface/request.html',context)
