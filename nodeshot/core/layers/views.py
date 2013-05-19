from rest_framework import generics
from rest_framework.views import APIView

from .models import Layer
from .serializers import *


class LayerList(generics.ListCreateAPIView):
    """
    ### GET
    
    Retrieve list of layers.
    """
    model= Layer
    serializer_class= LayerListSerializer
    queryset = Layer.objects.published()

list = LayerList.as_view()


class LayerDetail(generics.RetrieveAPIView):
    """
    ### GET
    
    Retrieve details of specified layer.
    """
    model= Layer
    serializer_class= LayerDetailSerializer
    queryset = Layer.objects.published()
    lookup_field = 'slug'

details = LayerDetail.as_view()

    
class LayerNodesList(generics.RetrieveAPIView):
    """
    ### GET
    
    Retrieve list of nodes of the specified layer
    """
    model = Layer
    serializer_class = LayerNodeListSerializer
    queryset = Layer.objects.published()
    lookup_field = 'slug'

node_list = LayerNodesList.as_view()