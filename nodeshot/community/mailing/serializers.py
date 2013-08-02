from rest_framework import serializers

from nodeshot.core.nodes.serializers import NodeDetailSerializer

from .models import Inward


__all__ = [
    'InwardMessageSerializer',
]


class InwardMessageSerializer(serializers.ModelSerializer):
    """ status icons """
    
    class Meta:
        model = Inward
        read_only_fields = (
            'status', 'added', 'updated', 'content_type', 'object_id',
            'user', 'ip', 'user_agent', 'accept_language')


#NodeDetailSerializer.contact = serializers.HyperlinkedIdentityField(view_name='api_node_contact', slug_field='slug')
#NodeDetailSerializer.base_fields['contact'] = serializers.HyperlinkedIdentityField(view_name='api_node_contact', slug_field='slug')
#NodeDetailSerializer.Meta.fields.append('contact')