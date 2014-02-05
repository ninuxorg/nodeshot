import datetime
import operator

from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.gis.geos import *

from rest_framework import generics, permissions, authentication, status
from rest_framework.views import APIView
from rest_framework.response import Response

from nodeshot.core.nodes.models import Node, Status, Image
from nodeshot.core.layers.models import Layer
from nodeshot.community.participation.models import Vote, Comment, Rating

from .base import SERVICES, iso8601_REGEXP
from .serializers import *

STATUS = {
            'Potenziale' : 'open',
            'Pianificato' : 'open',
            'Attivo' : 'closed',
        }

MODELS = {
            'node': Node,
            'vote': Vote,
            'comment': Comment,
            'rate': Rating,
        }

def get_service_name(service_code):
    return SERVICES[service_code]['name']

def create_output_data(data):
    pnt = fromstr(data['geometry'])
    del data['geometry']
    data['lng'] = pnt[0]
    data['lat'] = pnt[1]
    status_id = data['status']
    status = get_object_or_404(Status, pk=status_id)
    data['status'] = STATUS[status.name]
    return data

class ServiceList(generics.ListAPIView):
    """
    Retrieve list of Open 311 services.
    """
    authentication_classes = (authentication.SessionAuthentication,)
    serializer_class = ServiceListSerializer
    
    def get(self, request, *args, **kwargs):
        """ return several services for each layer """
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
                    context=context,
                    service_type=service_type
                ).data
            )
        
        return Response(services)

service_list = ServiceList.as_view()


class ServiceDefinition(APIView):
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
        data = serializers[service_type]().data
        
        return Response(data)
    
service_definition = ServiceDefinition.as_view()


class ServiceRequests(generics.ListCreateAPIView):
    """
    ### GET
    
    Retrieve requests.
    
    ####Parameters:
    
    service_code: defaults to 'node'
    
    status: 'open' or 'closed'
    
    start_date: date in w3 format, eg 2010-01-01T00:00:00Z
    
    end_date: date in w3 format, eg 2010-01-01T00:00:00Z
    
    ### POST
    
    Post a request
    """
    authentication_classes = (authentication.SessionAuthentication,)
    #serializer_class= NodeRequestListSerializer
    
    def get_serializer_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.serializer_class`.

        You may want to override this if you need to provide different
        serializations depending on the incoming request.

        (Eg. admins get full serialization, others get basic serialization)
        """
        service_code = 'node'
        
        serializers = {
            'node': NodeRequestListSerializer,
            'vote': VoteRequestDetailSerializer,
            'comment': CommentRequestDetailSerializer,
            'rate': RatingRequestDetailSerializer,
        }
        
        serializer_class = serializers[service_code]
        if serializer_class is not None:
            return serializer_class

        assert self.model is not None, \
            "'%s' should either include a 'serializer_class' attribute, " \
            "or use the 'model' attribute as a shortcut for " \
            "automatically generating a serializer class." \
            % self.__class__.__name__

        class DefaultSerializer(self.model_serializer_class):
            class Meta:
                model = self.model
        return DefaultSerializer
    
    def get_custom_data(self):
        """ additional request.DATA """
        
        return {
            'user': self.request.user.id
        }
    
    def get(self, request, *args, **kwargs):
        
        #if 'service_code' not in request.GET.keys():
        ##if not request.GET['service_code']:
        #    return Response({ 'detail': _('A service code must be inserted') }, status=404)
        #service_code = request.GET['service_code']
        #
        #if service_code not in SERVICES.keys():
        #    return Response({ 'detail': _('Service not found') }, status=404)
        
        service_code = 'node'
        start_date = None
        end_date = None
        status = None
                
        STATUSES = {}
        for status_type in ('open','closed'):
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
        
        #serializers = {
        #    'node': NodeRequestListSerializer,
        #    'vote': VoteRequestDetailSerializer,
        #    'comment': CommentRequestDetailSerializer,
        #    'rate': RatingRequestDetailSerializer,
        #}
        
        service_model = MODELS[service_code]
        self.queryset = service_model.objects.all()
        
        #Check of date parameters
        
        if start_date is not None and end_date is not None:
            self.queryset = self.queryset.filter(added__gte = start_date).filter(added__lte = end_date)
            
        if start_date is not None and end_date is None:
            self.queryset = self.queryset.filter(added__gte = start_date)
            
        if start_date is None and end_date is not None:
            self.queryset = self.queryset.filter(added__lte = end_date)
            
        #Check of status parameter
        
        if status is not None:
            q_list = [Q(status__name__exact = s) for s in STATUSES[status]]
            self.queryset = self.queryset.filter(reduce(operator.or_, q_list))            
                    
        ## init right serializer
        #kwargs['serializer'] = serializers[service_code]
        kwargs['service_code'] = service_code
        return self.list(request, *args, **kwargs)
    
    def list(self, request, *args, **kwargs):
        self.object_list = self.filter_queryset(self.get_queryset())
        service_code = kwargs['service_code']
        context = self.get_serializer_context()
        # Default is to allow empty querysets.  This can be altered by setting
        # `.allow_empty = False`, to raise 404 errors on empty querysets.
        if not self.allow_empty and not self.object_list:
            warnings.warn(
                'The `allow_empty` parameter is due to be deprecated. '
                'To use `allow_empty=False` style behavior, You should override '
                '`get_queryset()` and explicitly raise a 404 on empty querysets.',
                PendingDeprecationWarning
            )
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
    
    #def list(self, request, *args, **kwargs):
    #    self.object_list = self.filter_queryset(self.get_queryset())
    #
    #    # Default is to allow empty querysets.  This can be altered by setting
    #    # `.allow_empty = False`, to raise 404 errors on empty querysets.
    #    if not self.allow_empty and not self.object_list:
    #        warnings.warn(
    #            'The `allow_empty` parameter is due to be deprecated. '
    #            'To use `allow_empty=False` style behavior, You should override '
    #            '`get_queryset()` and explicitly raise a 404 on empty querysets.',
    #            PendingDeprecationWarning
    #        )
    #        class_name = self.__class__.__name__
    #        error_msg = self.empty_error % {'class_name': class_name}
    #        raise Http404(error_msg)
    #
    #    # Switch between paginated or standard style responses
    #    page = self.paginate_queryset(self.object_list)
    #    if page is not None:
    #        serializer = self.get_pagination_serializer(page)
    #    else:
    #        serializer = self.get_serializer(self.object_list, many=True)
    #
    #    return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
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
            #Get layer id
            layer=Layer.objects.get(slug=request.POST['layer'])           
            request.UPDATED['layer'] = layer.id
            
            #Transform coords in wkt geometry
            lat = float(request.UPDATED['lat'])
            lng = float(request.UPDATED['lng'])
            point = Point((lng,lat))
            request.UPDATED['geometry'] = point.wkt

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
            #print obj.id
            for file,image_file in files.iteritems():
                image=Image(node=obj, file=image_file)
                image.save()
    
    #def create(self, request, *args, **kwargs):
    #    serializer = self.get_serializer(data=request.DATA, files=request.FILES)
    #
    #    if serializer.is_valid():
    #        self.pre_save(serializer.object)
    #        self.object = serializer.save(force_insert=True)
    #        self.post_save(self.object, created=True)
    #        headers = self.get_success_headers(serializer.data)
    #        return Response(serializer.data, status=status.HTTP_201_CREATED,
    #                        headers=headers)
    #
    #    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
service_requests = ServiceRequests.as_view()


class ServiceRequest(generics.RetrieveAPIView):
    
    def get(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        service_code = kwargs['service_code']
        request_id = kwargs['request_id']
        
        if service_code not in SERVICES.keys():
            return Response({ 'detail': _('Service not found') }, status=404)
        
        serializers = {
            'node': NodeRequestDetailSerializer,
            'vote': VoteRequestDetailSerializer,
            'comment': CommentRequestDetailSerializer,
            'rate': RatingRequestDetailSerializer,
        }
        
        service_model = MODELS[service_code]
        request_object = get_object_or_404(service_model, pk=request_id)
        data = serializers[service_code](request_object,context=context).data
        
        if service_code == 'node':
            data = create_output_data(data)
        else:
            data['status'] = 'Closed'                       
        
        data['service_code'] = service_code
        data['service_name'] = SERVICES[service_code]['name']
        
        
        return Response(data)

service_request = ServiceRequest.as_view()



    

