from django.forms.fields import IntegerField
from django.forms.widgets import TextInput
from util import question, encode


class MathWidget(TextInput):
    """
    Text input for a math captcha field. Stores hashed answer in hidden ``math_captcha_question`` field
    """
    def render(self, name, value, attrs):
        aquestion = question()
        value = super(MathWidget, self).render(name, value, attrs)
        hidden = '<input type="hidden" value="%s" name="math_captcha_question"/>' %  encode(aquestion)
        return value.replace('<input', '%s %s = <input' % (hidden, aquestion))
        
class MathField(IntegerField):
    widget = MathWidget()

    def __init__(self, *a, **kw):
        super(MathField, self).__init__(None, 0, *a, **kw)        