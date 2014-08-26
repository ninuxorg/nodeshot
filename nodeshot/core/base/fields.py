# snippet "MultiSelectField with comma separated values (Field + FormField)"
# http://djangosnippets.org/snippets/2753/

# New version of this snippet http://djangosnippets.org/snippets/1200/
# tested with Django 1.4

from django import forms
from django.db import models
from django.utils.text import capfirst
from django.core import exceptions
from django.conf import settings


class MultiSelectFormField(forms.MultipleChoiceField):
    widget = forms.CheckboxSelectMultiple
 
    def __init__(self, *args, **kwargs):
        self.max_choices = kwargs.pop('max_choices', 0)
        super(MultiSelectFormField, self).__init__(*args, **kwargs)
 
    def clean(self, value):
        if not value and self.required:
            raise forms.ValidationError(self.error_messages['required'])
        # if value and self.max_choices and len(value) > self.max_choices:
        #     raise forms.ValidationError('You must select a maximum of %s choice%s.'
        #             % (apnumber(self.max_choices), pluralize(self.max_choices)))
        return value

 
class MultiSelectField(models.Field):
    __metaclass__ = models.SubfieldBase
 
    def get_internal_type(self):
        return "CharField"
 
    def get_choices_default(self):
        return self.get_choices(include_blank=False)
 
    def _get_FIELD_display(self, field):
        value = getattr(self, field.attname)
        choicedict = dict(field.choices)
        return choicedict.get(value, value)
 
    def formfield(self, **kwargs):
        # don't call super, as that overrides default widget if it has choices
        defaults = {'required': not self.blank, 'label': capfirst(self.verbose_name),
                    'help_text': self.help_text, 'choices': self.choices}
        if self.has_default():
            defaults['initial'] = self.get_default()
        defaults.update(kwargs)
        return MultiSelectFormField(**defaults)

    def get_prep_value(self, value):
        return value

    def get_db_prep_value(self, value, connection=None, prepared=False):
        if isinstance(value, basestring):
            return value
        elif isinstance(value, list):
            return ",".join(value)
 
    def to_python(self, value):
        if value is not None:
            return value if isinstance(value, list) else value.split(',')
        return ''

    def contribute_to_class(self, cls, name):
        super(MultiSelectField, self).contribute_to_class(cls, name)
        if self.choices:
            func = lambda self, fieldname = name, choicedict = dict(self.choices): ",".join([
                choicedict.get(value, value) for value in getattr(self, fieldname)
            ])
            setattr(cls, 'get_%s_display' % self.name, func)
 
    def validate(self, value, model_instance):
        arr_choices = self.get_choices_selected(self.get_choices_default())
        try:
            for opt_select in value:
                if (int(opt_select) not in arr_choices):  # the int() here is for comparing with integer choices
                    raise exceptions.ValidationError(self.error_messages['invalid_choice'] % value)
        except ValueError:
            if not self.blank:
                raise exceptions.ValidationError(self.error_messages['invalid_choice'] % value)
        return
 
    def get_choices_selected(self, arr_choices=''):
        if not arr_choices:
            return False
        list = []
        for choice_selected in arr_choices:
            list.append(choice_selected[0])
        return list
 
    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)


# taken from django-colorful
# https://github.com/charettes/django-colorful
import re
from django.forms.fields import RegexField
from .widgets import ColorFieldWidget

RGB_REGEX = re.compile('^#?((?:[0-F]{3}){1,2})$', re.IGNORECASE)

class RGBColorField(models.CharField):

    widget = ColorFieldWidget

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 7
        super(RGBColorField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs.update({
                       'form_class': RegexField,
                       'widget': self.widget,
                       'regex': RGB_REGEX
                       })
        return super(RGBColorField, self).formfield(**kwargs)


# needed for South compatibility
if 'south' in settings.INSTALLED_APPS:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^coop\.utils\.fields\.MultiSelectField"])
    add_introspection_rules([], ["^nodeshot\.core\.base\.fields\.RGBColorField"])