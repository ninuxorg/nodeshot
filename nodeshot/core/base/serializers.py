from django.core.urlresolvers import NoReverseMatch

from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.response import Response


class ModelValidationSerializer(serializers.ModelSerializer):
    """ calls clean method of model automatically """
    def validate(self, data):
        # if instance hasn't been created yet
        if not self.instance:
            instance = self.Meta.model(**data)
            instance.clean()
        # if modifying an existing instance
        else:
            for key, value in data.items():
                setattr(self.instance, key, value)
            self.instance.clean()
        return data


class DynamicRelationshipsMixin(object):
    """
    Django Rest Framework Serializer Mixin
    which adds the possibility to dynamically add relationships to a serializer.

    To add a relationship, use the class method "add_relationship", this way:

    >>> SerializerName.add_relationship('relationship_name', 'view_name', 'lookup_field')

    for example:

    >>> from nodeshot.core.nodes.serializers import NodeDetailSerializer
    >>> NodeDetailSerializer.add_relationship(**{
        'name': 'comments',
        'view_name': 'api_node_comments',
        'lookup_field': 'slug'
    })
    """
    _relationships = {}

    @classmethod
    def add_relationship(_class, name,
                         view_name=None, lookup_field=None,
                         serializer=None, many=False, queryset=None,
                         function=None):
        """ adds a relationship to serializer
        :param name: relationship name (dictionary key)
        :type name: str
        :param view_name: view name as specified in urls.py
        :type view_name: str
        :param lookup_field: lookup field, usually slug or id/pk
        :type lookup_field: str
        :param serializer: Serializer class to use for relationship
        :type serializer: Serializer
        :param many: indicates if it's a list or a single element, defaults to False
        :type many: bool
        :param queryset: queryset string representation to use for the serializer
        :type queryset: QuerySet
        :param function: function that returns the value to display (dict, list or str)
        :type function: function(obj, request)
        :returns: None
        """
        if view_name is not None and lookup_field is not None:
            _class._relationships[name] = {
                'type': 'link',
                'view_name': view_name,
                'lookup_field': lookup_field
            }
        elif serializer is not None and queryset is not None:
            _class._relationships[name] = {
                'type': 'serializer',
                'serializer': serializer,
                'many': many,
                'queryset': queryset
            }
        elif function is not None:
            _class._relationships[name] = {
                'type': 'function',
                'function': function
            }
        else:
            raise ValueError('missing arguments, either pass view_name and lookup_field or serializer and queryset')

    def get_lookup_value(self, obj, string):
        if '.' in string:
            if '()' in string:
                string = string.replace('()', '')
                is_method = True
            else:
                is_method = False
            levels = string.split('.')
            value = getattr(obj, levels.pop(0))
            if value is not None:
                for level in levels:
                    value = getattr(value, level)
                if is_method:
                    return value()
                else:
                    return value
            else:
                return None
        else:
            return getattr(obj, string)

    def get_relationships(self, obj):
        request = self.context['request']
        format = self.context['format']
        relationships = {}
        # loop over private _relationship attribute
        for key, options in self._relationships.iteritems():
            # if relationship is a link
            if options['type'] == 'link':
                # get lookup value
                lookup_value = self.get_lookup_value(obj, options['lookup_field'])
                # get URL
                value = reverse(options['view_name'],
                                args=[lookup_value],
                                request=request,
                                format=format)
            # if relationship is a serializer
            elif options['type'] == 'serializer':
                queryset = options['queryset'](obj, request)
                # get serializer representation
                value = options['serializer'](instance=queryset,
                                              context=self.context,
                                              many=options['many']).data
            elif options['type'] == 'function':
                value = options['function'](obj, request)
            else:
                raise ValueError('type %s not recognized' % options['type'])
            # populate new dictionary with value
            relationships[key] = value
        return relationships


class HyperlinkedField(serializers.RelatedField):
    """
    shortcut for reversing urls in serializers
    """
    def __init__(self, view_name, *args, **kwargs):
        kwargs['read_only'] = True
        kwargs['source'] = '*'
        self.view_name = view_name
        super(HyperlinkedField, self).__init__(*args, **kwargs)

    def to_representation(self, value):
        return reverse(self.view_name,
                       args=self.context['view'].kwargs,
                       request=self.context['request'],
                       format=self.context['format'])
