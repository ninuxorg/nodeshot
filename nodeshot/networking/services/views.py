from rest_framework import permissions, authentication, generics

from nodeshot.core.base.mixins import ACLMixin

from .serializers import *
from .models import *


class ServiceList(ACLMixin, generics.ListCreateAPIView):
    """
    Retrieve service list according to user access level
    
    Parameters:
    
     * `limit=<n>`: specify number of items per page (defaults to 40)
     * `limit=0`: turns off pagination
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    model = Service
    queryset = Service.objects.all()
    serializer_class = ServiceListSerializer
    pagination_serializer_class = PaginatedServiceSerializer
    paginate_by_param = 'limit'
    paginate_by = 40
    
service_list = ServiceList.as_view()


class ServiceDetail(ACLMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve service detail according to user access level
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    model = Service
    queryset = Service.objects.all()
    serializer_class = ServiceDetailSerializer
    
service_details = ServiceDetail.as_view()


class CategoryList(generics.ListCreateAPIView):
    """
    List of service categories
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    model = Category
    serializer_class = CategorySerializer
    
service_category_list = CategoryList.as_view()


class CategoryDetail(generics.RetrieveUpdateAPIView):
    """
    Category detail view
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    model = Category
    serializer_class = CategorySerializer
    
service_category_details = CategoryDetail.as_view()
