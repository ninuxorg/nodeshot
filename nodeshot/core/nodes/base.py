from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
User = get_user_model()

from rest_framework import serializers, generics
from rest_framework_gis import serializers as geoserializers
from rest_framework_hstore.serializers import HStoreSerializer

from nodeshot.core.base.serializers import DynamicRelationshipsMixin
from nodeshot.core.base.mixins import ACLMixin
from nodeshot.core.layers.models import Layer

from .settings import REVERSION_ENABLED


class ExtensibleNodeSerializer(DynamicRelationshipsMixin, HStoreSerializer):
    """ node detail """
    layer = serializers.SlugRelatedField(slug_field='slug',
                                         queryset=Layer.objects.all())
    layer_name = serializers.ReadOnlyField(source='layer.name')
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    status = serializers.SlugRelatedField(slug_field='slug', read_only=True)
    geometry = geoserializers.GeometryField(label=_('coordinates'))
    access_level = serializers.ReadOnlyField(source='get_access_level_display')
    relationships = serializers.SerializerMethodField()
    # this is needed to avoid adding stuff to DynamicRelationshipsMixin
    _relationships = {}


if REVERSION_ENABLED:
    from nodeshot.core.base.mixins import RevisionCreate, RevisionUpdate

    class ListCreateAPIView(ACLMixin, RevisionCreate, generics.ListCreateAPIView):
        pass

    class RetrieveUpdateDestroyAPIView(ACLMixin, RevisionUpdate, generics.RetrieveUpdateDestroyAPIView):
        pass
else:
    class ListCreateAPIView(ACLMixin, generics.ListCreateAPIView):
        pass

    class RetrieveUpdateDestroyAPIView(ACLMixin, generics.RetrieveUpdateDestroyAPIView):
        pass
