import simplejson as json

#from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework import generics, authentication
from rest_framework.response import Response

from nodeshot.core.base.mixins import ACLMixin

from .serializers import *
from .models import *


class PageList(ACLMixin, generics.ListAPIView):
    """
    ### GET
    
    Retrieve the list of pages.
    """
    authentication_classes = (authentication.SessionAuthentication,)
    queryset = Page.objects.published()
    serializer_class = PageListSerializer
    
page_list = PageList.as_view()


class PageDetail(ACLMixin, generics.RetrieveAPIView):
    """
    ### GET
    
    Retrieve specified page.
    """
    authentication_classes = (authentication.SessionAuthentication,)
    queryset = Page.objects.published()
    serializer_class = PageDetailSerializer
    
page_detail = PageDetail.as_view()


# ------ Menu ------ #


class MenuList(ACLMixin, generics.ListAPIView):
    """
    ### GET
    
    Retrieve the list of pages.
    """
    authentication_classes = (authentication.SessionAuthentication,)
    queryset = MenuItem.objects.published()
    serializer_class = MenuSerializer
    
menu_list = MenuList.as_view()