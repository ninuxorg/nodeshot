from rest_framework import pagination, serializers
from rest_framework_gis import serializers as gis_serializers

from .models import *


__all__ = [
    'DeviceSerializer',
    'PaginatedDeviceSerializer',
    # GeoFeatureSerializer
    #'LocationGeoFeatureSerializer',
    #'PaginatedLocationGeoFeatureSerializer',
]

  
class DeviceSerializer(gis_serializers.GeoModelSerializer):
    """ location geo serializer  """
    
    #geometry = gis_serializers.GeometryField(required=True)
    
    #details = serializers.HyperlinkedIdentityField(view_name='api_location_details')
    
    class Meta:
        model = Device
        exclude = ('shortcuts', )


class PaginatedDeviceSerializer(pagination.PaginationSerializer):
    
    class Meta:
        object_serializer_class = DeviceSerializer


#class LocationGeoFeatureSerializer(gis_serializers.GeoFeatureModelSerializer):
#    """ location geo serializer  """
#    
#    details = serializers.HyperlinkedIdentityField(view_name='api_geojson_location_details')
#    fancy_name = serializers.SerializerMethodField('get_fancy_name')
#    
#    def get_fancy_name(self, obj):
#        return u'Kool %s' % obj.name
#    
#    class Meta:
#        model = Location
#        geo_field = 'geometry'
#
#
#class PaginatedLocationGeoFeatureSerializer(pagination.PaginationSerializer):
#    
#    class Meta:
#        object_serializer_class = LocationGeoFeatureSerializer