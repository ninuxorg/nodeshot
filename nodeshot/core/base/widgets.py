# -*- coding: utf-8 -*-
from django.utils.safestring import mark_safe
from django.utils.html import escape, conditional_escape
from django.utils.encoding import force_unicode
from django.forms.widgets import ClearableFileInput, CheckboxInput
from django.utils.translation import ugettext as _


class AdvancedFileInput(ClearableFileInput):
    """
    File Input Widget
    """

    def __init__(self, *args, **kwargs):

        self.url_length = kwargs.pop('url_length',30)
        self.preview = kwargs.pop('preview',True)
        self.image_width = kwargs.pop('image_width',200)
        super(AdvancedFileInput, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None,):

        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
        }
        template = u'%(input)s'

        substitutions['input'] = super(ClearableFileInput, self).render(name, value, attrs)

        if value and hasattr(value, "url"):

            template = self.template_with_initial
            if self.preview:
                substitutions['initial'] = (u'<a href="{0}">{1}</a><br /><br />\
                <a href="{0}" target="_blank"><img src="{0}" alt="" width="{2}" /></a><br /><br />'.format
                    (escape(value.url),'...'+escape(force_unicode(value))[-self.url_length:],
                     self.image_width))
            else:
                substitutions['initial'] = (u'<a href="{0}">{1}</a>'.format
                    (escape(value.url),'...'+escape(force_unicode(value))[-self.url_length:]))
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(checkbox_id)
                substitutions['clear'] = CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = self.template_with_clear % substitutions

        return mark_safe(template % substitutions)


# originally taken from django-colorful but adapted

from django.conf import settings
from django.forms.widgets import TextInput
from django.utils.safestring import SafeUnicode

try:
    url = settings.STATIC_URL
except AttributeError:
    try:
        url = settings.MEDIA_URL
    except AttributeError:
        url = ''

class ColorFieldWidget(TextInput):
    class Media:
        css = {
            'all': ("%scolorful/spectrum.css" % url,)
        }
        js  = ("%scolorful/spectrum.js" % url,)

    input_type = 'color'

    def render_script(self, id):
        return u'''<script type="text/javascript">
                    (function($){
                        $(document).ready(function(){
                            $('#%s').each(function(i, elm){
                                // Make sure html5 color element is not replaced
                                if(elm.type != 'color'){
                                    $(elm).spectrum({
                                        showInput: true,
                                        showInitial: true,
                                        cancelText: '%s',
                                        chooseText: '%s'
                                    });
                                }
                            });
                        });
                    })('django' in window ? django.jQuery : jQuery);
                </script>
                ''' % (id, _('cancel'), _('ok'))

    def render(self, name, value, attrs={}):
        if 'id' not in attrs:
            attrs['id'] = "#id_%s" % name
        render = super(ColorFieldWidget, self).render(name, value, attrs)
        return SafeUnicode(u"%s%s" % (render, self.render_script(attrs['id'])))
