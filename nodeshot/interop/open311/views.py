import operator

from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.gis.geos import Point, fromstr
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from rest_framework import generics, permissions, authentication, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from nodeshot.core.nodes.models import Node, Status, Image
from nodeshot.core.layers.models import Layer

from .base import SERVICES, DISCOVERY, MODELS, iso8601_REGEXP
from .settings import STATUS
from .serializers import *


@api_view(['GET'])
def service_discovery(request):
    """
    Open 311 services' discovery.
    """
    return Response(DISCOVERY)


class ServiceDefinitionList(generics.ListAPIView):
    """
    Retrieve list of Open 311 services.
    """
    authentication_classes = (authentication.SessionAuthentication,)
    serializer_class = ServiceListSerializer

    def get(self, request, *args, **kwargs):
        """ return list of open 311 services  """
        # init django rest framework specific stuff
        serializer_class = self.get_serializer_class()
        context = self.get_serializer_context()

        # init empty list
        services = []

        # loop over each service
        for service_type in SERVICES.keys():
            # initialize serializers for layer
            services.append(
                serializer_class(
                    object(),
                    context=context,
                    service_type=service_type
                ).data
            )

        return Response(services)

service_definition_list = ServiceDefinitionList.as_view()


class ServiceDefinitionDetail(APIView):
    """
    Retrieve details of specified service.
    """

    def get(self, request, *args, **kwargs):
        service_type = kwargs['service_type']

        if service_type not in SERVICES.keys():
            return Response({ 'detail': _('Not found') }, status=404)

        serializers = {
            'node': ServiceNodeSerializer,
            'vote': ServiceVoteSerializer,
            'comment': ServiceCommentSerializer,
            'rate': ServiceRatingSerializer,
        }

        # init right serializer
        data = serializers[service_type](object()).data

        return Response(data)

service_definition_detail = ServiceDefinitionDetail.as_view()


def create_output_data(data):
    # convert received geometry to Point
    geom = fromstr(data['geometry']).centroid
    del data['geometry']
    data['long'] = geom[0]
    data['lat'] = geom[1]

    # get status from model and converts it into the mapped status type (open/closed)
    status_id = data['status']
    status = get_object_or_404(Status, pk=status_id)
    data['detailed_status'] = status.name
    data['detailed_status_description'] = status.description
    try:
        data['status'] = STATUS[status.slug]
    except KeyError:
        if settings.DEBUG:
            raise ImproperlyConfigured("NODESHOT['OPEN311']['STATUS'] settings bad configuration: key %s not found"
                                       % status.slug)
        else:
            data['status'] = 'closed'

    return data


class ServiceRequestList(generics.ListCreateAPIView):
    """
    ### GET
    ###Retrieve list of service requests.

    Required parameters:

     * `service_code=<string>`: possible values are: 'node', 'vote', 'rate' , 'comment'

    ####Note:    List is displayed only for 'node' service requests

    Optional  parameters ( relevant only if service_code = node ):

     * `status=<string>`: possible values are: 'open' or 'closed'
     * `start_date=<date>`: date in w3 format, eg 2010-01-01T00:00:00Z
     * `end_date=<date>`: date in w3 format, eg 2010-01-01T00:00:00Z
     * `layer=<layer>`: layer to which node belongs

    ### POST
    ### Create a new service request. Requires authentication.
    See service definition for required parameters
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class= NodeRequestListSerializer
    model = Node

    def get_serializer(self, instance=None, data=None,
                       files=None, many=False, partial=False):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializers = {
            'node': NodeRequestListSerializer,
            'vote': VoteRequestListSerializer,
            'comment': CommentRequestListSerializer,
            'rate': RatingRequestListSerializer,
        }
        context = self.get_serializer_context()
        service_code = context['request'].QUERY_PARAMS.get('service_code', 'node')

        if service_code not in serializers.keys():
            serializer_class = self.get_serializer_class()
        else:
            serializer_class = serializers[service_code]

        return serializer_class(instance, data=data, files=files,
                                many=many, partial=partial, context=context)

    def get_custom_data(self):
        """ additional request.DATA """

        return {
            'user': self.request.user.id
        }

    def get(self, request, *args, **kwargs):
        """ Retrieve list of service requests """
        if 'service_code' not in request.GET.keys():
            return Response({ 'detail': _('A service code must be inserted') }, status=404)

        service_code = request.GET['service_code']

        if service_code not in SERVICES.keys():
            return Response({ 'detail': _('Service not found') }, status=404)

        start_date = None
        end_date = None
        status = None
        layer = None

        STATUSES = {}
        for status_type in ('open', 'closed'):
            STATUSES[status_type] = [k for k, v in STATUS.items() if v == status_type]

        if 'start_date' in request.GET.keys():
            start_date = request.GET['start_date']
            if iso8601_REGEXP.match(start_date) is None:
                return Response({ 'detail': _('Invalid date inserted') }, status=404)

        if 'end_date' in request.GET.keys():
            end_date = request.GET['end_date']
            if iso8601_REGEXP.match(end_date) is None:
                return Response({ 'detail': _('Invalid date inserted') }, status=404)

        if 'status' in request.GET.keys():
            if request.GET['status'] not in ('open','closed'):
                return Response({ 'detail': _('Invalid status inserted') }, status=404)
            status = request.GET['status']

        if 'layer' in request.GET.keys():
            layer = request.GET['layer']
            node_layer = get_object_or_404(Layer, slug=layer)

        service_model = MODELS[service_code]
        if service_code in ('vote', 'comment', 'rate'):
            self.queryset = service_model.objects.none()
        else:
            self.queryset = service_model.objects.all()

            # Filter by layer
            if layer is not None:
                self.queryset = self.queryset.filter(layer = node_layer)

            # Check of date parameters
            if start_date is not None and end_date is not None:
                self.queryset = self.queryset.filter(added__gte = start_date).filter(added__lte = end_date)

            if start_date is not None and end_date is None:
                self.queryset = self.queryset.filter(added__gte = start_date)

            if start_date is None and end_date is not None:
                self.queryset = self.queryset.filter(added__lte = end_date)

        # Check of status parameter
        if status is not None:
            q_list = [Q(status__slug__exact = s) for s in STATUSES[status]]
            self.queryset = self.queryset.filter(reduce(operator.or_, q_list))

        # init right serializer
        kwargs['service_code'] = service_code

        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        self.object_list = self.filter_queryset(self.get_queryset())
        service_code = kwargs['service_code']

        # Default is to allow empty querysets.  This can be altered by setting
        # `.allow_empty = False`, to raise 404 errors on empty querysets.
        if not self.allow_empty and not self.object_list:
            class_name = self.__class__.__name__
            error_msg = self.empty_error % {'class_name': class_name}
            raise Http404(error_msg)

        # Switch between paginated or standard style responses
        page = self.paginate_queryset(self.object_list)

        if page is not None:
            serializer = self.get_pagination_serializer(page)
        else:
            serializer = self.get_serializer(self.object_list, many=True)

        data = serializer.data

        if service_code == 'node':
            for item in data:
                item = create_output_data(item)
        else:
            pass

        return Response(data)

    def post(self, request, *args, **kwargs):
        """ Post a service request ( requires authentication) """

        service_code = request.POST['service_code']

        if service_code not in SERVICES.keys():
            return Response({ 'detail': _('Service not found') }, status=404)

        serializers = {
            'node': NodeRequestSerializer,
            'vote': VoteRequestSerializer,
            'comment': CommentRequestSerializer,
            'rate': RatingRequestSerializer,
        }

        # init right serializer
        kwargs['service_code'] = service_code
        kwargs['serializer'] = serializers[service_code]

        user=self.get_custom_data()
        request.UPDATED = request.POST.copy()
        request.UPDATED['user'] = user['user']
        if service_code == 'node':
            for checkPOSTdata in ('layer','name','lat','long'):
                # Check if mandatory parameters key exists
                if checkPOSTdata not in request.POST.keys():
                    return Response({ 'detail': _('Mandatory parameter not found') }, status=400)
                else:
                    # Check if mandatory parameters values have been inserted
                    if not request.POST[checkPOSTdata] :
                        return Response({ 'detail': _('Mandatory parameter not found') }, status=400)
            # Get layer id
            layer = Layer.objects.get(slug=request.UPDATED['layer'])
            request.UPDATED['layer'] = layer.id

            # Transform coords in wkt geometry
            lat = float(request.UPDATED['lat'])
            long = float(request.UPDATED['long'])
            point = Point((long, lat))
            request.UPDATED['geometry'] = point.wkt
            request.UPDATED['slug'] = slugify(request.UPDATED['name'])

        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):

        serializer = kwargs['serializer']( data=request.UPDATED, files=request.FILES)
        service_code= kwargs['service_code']
        if serializer.is_valid():
            self.pre_save(serializer.object)
            self.object = serializer.save(force_insert=True)
            self.post_save(self.object, created=True,
                           files=request.FILES,
                           service_code=service_code
                           )
            headers = self.get_success_headers(serializer.data)
            response_311 = service_code + '-' + str(self.object.id)
            return Response(response_311, status=status.HTTP_201_CREATED,
                            headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post_save(self,obj, created, files, service_code):
        if service_code == 'node' and files:
            for file,image_file in files.iteritems():
                image=Image(node=obj, file=image_file)
                image.save()

service_request_list = ServiceRequestList.as_view()


class ServiceRequestDetail(generics.RetrieveAPIView):
    """ Retrieve the details of a service request """

    serializer_class= NodeRequestDetailSerializer

    def get(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        service_code = kwargs['service_code']
        request_id = kwargs['request_id']

        if service_code not in SERVICES.keys():
            return Response({ 'detail': _('Service not found') }, status=404)

        serializers = {
            'node': NodeRequestDetailSerializer,
            'vote': VoteRequestSerializer,
            'comment': CommentRequestSerializer,
            'rate': RatingRequestSerializer,
        }

        service_model = MODELS[service_code]
        request_object = get_object_or_404(service_model, pk=request_id)
        data = serializers[service_code](request_object, context=context).data

        if service_code == 'node':
            data = create_output_data(data)
        else:
            data['status'] = 'Closed'

        data['service_code'] = service_code
        data['service_name'] = SERVICES[service_code]['name']

        return Response(data)

service_request_detail = ServiceRequestDetail.as_view()
