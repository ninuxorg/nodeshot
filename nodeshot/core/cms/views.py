from rest_framework import generics, authentication

from nodeshot.core.base.mixins import ACLMixin

# cache
from rest_framework_extensions.cache.decorators import cache_response
from nodeshot.core.base.cache import cache_by_group

from .serializers import *
from .models import *


class PageList(ACLMixin, generics.ListAPIView):
    """
    Retrieve the list of all the available pages.
    """
    authentication_classes = (authentication.SessionAuthentication,)
    queryset = Page.objects.published()
    serializer_class = PageListSerializer

    @cache_response(86400, key_func=cache_by_group)
    def get(self, request, *args, **kwargs):
        return super(PageList, self).get(request, *args, **kwargs)

page_list = PageList.as_view()


class PageDetail(ACLMixin, generics.RetrieveAPIView):
    """
    Retrieve specified page.
    """
    authentication_classes = (authentication.SessionAuthentication,)
    queryset = Page.objects.published()
    serializer_class = PageDetailSerializer

    @cache_response(86400, key_func=cache_by_group)
    def get(self, request, *args, **kwargs):
        return super(PageDetail, self).get(request, *args, **kwargs)

page_detail = PageDetail.as_view()


# ------ Menu ------ #


class MenuList(ACLMixin, generics.ListAPIView):
    """
    Retrieve menu item list.
    """
    authentication_classes = (authentication.SessionAuthentication,)
    queryset = MenuItem.objects.published().filter(parent=None)
    serializer_class = MenuSerializer

    @cache_response(86400, key_func=cache_by_group)
    def get(self, request, *args, **kwargs):
        return super(MenuList, self).get(request, *args, **kwargs)

menu_list = MenuList.as_view()
