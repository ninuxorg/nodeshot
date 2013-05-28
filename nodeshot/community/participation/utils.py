from django.core.exceptions import ObjectDoesNotExist
from nodeshot.core.nodes.models import Node


#def check_node(a,b):
#    try:
#        node = a.objects.get(pk=b)
#    except (a.DoesNotExist):
#        print('nuncesta')
#    return

# TODO

def is_participated(node_id):
    """ """
    from nodeshot.community.participation.models import NodeRatingCount
    n = Node.objects.get(pk=node_id)
    print(n.name)
    print(n.id)
    try:
        p=n.noderatingcount
    except ObjectDoesNotExist:
        print('no relation')
        nrc=NodeRatingCount(node=n)
        nrc.save()
        #return True
    #return False
    

