from django.core.urlresolvers import NoReverseMatch

from rest_framework import serializers
from rest_framework.fields import Field
from rest_framework.reverse import reverse


class ExtensibleModelSerializerOptions(serializers.SerializerOptions):
    """
    Meta class options for ExtensibleModelSerializerOptions
    """
    def __init__(self, meta):
        super(ExtensibleModelSerializerOptions, self).__init__(meta)
        self.model = getattr(meta, 'model', None)
        self.read_only_fields = getattr(meta, 'read_only_fields', ())
        self.non_native_fields = getattr(meta, 'non_native_fields', ())


class ExtensibleModelSerializer(serializers.ModelSerializer):
    """
    ModelSerializer in which non native extra fields can be specified.
    """
    
    _options_class = ExtensibleModelSerializerOptions
    
    def restore_object(self, attrs, instance=None):
        """
        Deserialize a dictionary of attributes into an object instance.
        You should override this method to control how deserialized objects
        are instantiated.
        """
        
        for field in self.opts.non_native_fields:
            attrs.pop(field)
        
        return super(ExtensibleModelSerializer, self).restore_object(attrs, instance)
    
    def to_native(self, obj):
        """
        Serialize objects -> primitives.
        """
        ret = self._dict_class()
        ret.fields = {}

        for field_name, field in self.fields.items():
            if field_name in self.opts.non_native_fields:
                continue
            field.initialize(parent=self, field_name=field_name)
            key = self.get_field_key(field_name)
            value = field.field_to_native(obj, field_name)
            ret[key] = value
            ret.fields[key] = field
        return ret


class HyperlinkedField(Field):
    """
    Represents the instance, or a property on the instance, using hyperlinking.
    """
    read_only = True

    def __init__(self, *args, **kwargs):
        self.view_name = kwargs.pop('view_name', None)
        # Optionally the format of the target hyperlink may be specified
        self.format = kwargs.pop('format', None)

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
            return reverse(view_name, request=request, format=format)
        except NoReverseMatch:
            pass

        raise Exception('Could not resolve URL for field using view name "%s"' % view_name)