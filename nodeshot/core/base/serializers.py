from django.core.urlresolvers import NoReverseMatch

from rest_framework import serializers
from rest_framework.fields import Field
from rest_framework.reverse import reverse


class ExtraFieldSerializerOptions(serializers.ModelSerializerOptions):
    """
    Meta class options for ExtraFieldSerializerOptions
    """
    def __init__(self, meta):
        super(ExtraFieldSerializerOptions, self).__init__(meta)
        self.non_native_fields = getattr(meta, 'non_native_fields', ())


# TODO: rename / remove
class ExtraFieldSerializer(serializers.ModelSerializer):
    """
    ModelSerializer in which non native extra fields can be specified.
    """

    _options_class = ExtraFieldSerializerOptions

    def restore_object(self, attrs, instance=None):
        """
        Deserialize a dictionary of attributes into an object instance.
        You should override this method to control how deserialized objects
        are instantiated.
        """
        for field in self.opts.non_native_fields:
            attrs.pop(field)

        return super(ExtraFieldSerializer, self).restore_object(attrs, instance)

    def to_native(self, obj):
        """
        Serialize objects -> primitives.
        """
        ret = self._dict_class()
        ret.fields = self._dict_class()

        for field_name, field in self.fields.items():
            if field.read_only and obj is None:
                continue
            field.initialize(parent=self, field_name=field_name)
            key = self.get_field_key(field_name)

            # skips to next iteration but permits to show the field in API browser
            try:
                value = field.field_to_native(obj, field_name)
            except AttributeError as e:
                if field_name in self.opts.non_native_fields:
                    continue
                else:
                    raise AttributeError(e.message)

            method = getattr(self, 'transform_%s' % field_name, None)
            if callable(method):
                value = method(obj, value)
            if not getattr(field, 'write_only', False):
                ret[key] = value
            ret.fields[key] = self.augment_field(field, field_name, key, value)

        return ret


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


class HyperlinkedField(Field):
    """
    Represents the instance, or a property on the instance, using hyperlinking.
    """
    read_only = True

    def __init__(self, *args, **kwargs):
        self.view_name = kwargs.pop('view_name', None)
        # Optionally the format of the target hyperlink may be specified
        self.format = kwargs.pop('format', None)
        # Optionally specify arguments
        self.view_args = kwargs.pop('view_args', None)

        super(HyperlinkedField, self).__init__(*args, **kwargs)

    def field_to_native(self, obj, field_name):
        request = self.context.get('request', None)
        format = self.context.get('format', None)
        view_name = self.view_name

        # By default use whatever format is given for the current context
        # unless the target is a different type to the source.
        if format and self.format and self.format != format:
            format = self.format

        try:
            return reverse(view_name, args=self.view_args, request=request, format=format)
        except NoReverseMatch:
            pass

        raise Exception('Could not resolve URL for field using view name "%s"' % view_name)


class GeoJSONDefaultObjectSerializer(serializers.Field):
    """
    If no object serializer is specified, then this serializer will be applied
    as the default.
    """

    def __init__(self, source=None, context=None):
        # Note: Swallow context kwarg - only required for eg. ModelSerializer.
        super(GeoJSONDefaultObjectSerializer, self).__init__(source=source)


class GeoJSONPaginationSerializerOptions(serializers.SerializerOptions):
    """
    An object that stores the options that may be provided to a
    pagination serializer by using the inner `Meta` class.

    Accessible on the instance as `serializer.opts`.
    """
    def __init__(self, meta):
        super(GeoJSONPaginationSerializerOptions, self).__init__(meta)
        self.object_serializer_class = getattr(meta, 'object_serializer_class',
                                               GeoJSONDefaultObjectSerializer)


class GeoJSONBasePaginationSerializer(serializers.Serializer):
    """
    A custom class for geojson serializers.
    """
    _options_class = GeoJSONPaginationSerializerOptions
    results_field = 'features'

    def __init__(self, *args, **kwargs):
        """
        Override init to add in the object serializer field on-the-fly.
        """
        super(GeoJSONBasePaginationSerializer, self).__init__(*args, **kwargs)
        results_field = self.results_field
        object_serializer = self.opts.object_serializer_class
        if 'context' in kwargs:
            context_kwarg = {'context': kwargs['context']}
        else:
            context_kwarg = {}

        self.fields[results_field] = object_serializer(source='object_list', **context_kwarg)


class GeoJSONPaginationSerializer(GeoJSONBasePaginationSerializer):
    """
    A geoJSON implementation of a pagination serializer.
    """
    type = serializers.SerializerMethodField('get_type')

    def get_type(self, obj):
        """ returns FeatureCollection type for geojson """
        return "FeatureCollection"
