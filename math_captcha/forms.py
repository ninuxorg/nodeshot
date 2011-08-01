from django import forms
from fields import MathField
from util import encode, decode
import settings


class NullWidget(forms.widgets.HiddenInput):
    def render(self, *a, **kw):
        return ''

def math_clean(form):
    """
    Cleans a form, validating answer to math question in the process.
    The given ``form`` must be an instance of either ``MathCaptchaModelForm`` or ``MathCaptchaForm``.
    Answer keys are communicated in the ``math_captcha_question`` field which is evaluated to give the correct answer
    after being validated against the ``SECRET_KEY``
    """
    try:
        value = form.cleaned_data['math_captcha_field']
        test_secret, question = decode(form.cleaned_data['math_captcha_question'])
        assert len(test_secret) == 40 and question
    except (TypeError, AssertionError):
        # problem decoding, junky data
        raise forms.ValidationError('Invalid token')
    except KeyError:
        return
    
    if encode(question) != form.cleaned_data['math_captcha_question']:
        # security problem, hack attempt
        raise forms.ValidationError('Invalid token')
    if eval(question) != value:
        raise forms.ValidationError('Wrong answer, try again')
        

class MathCaptchaModelForm(forms.ModelForm):
    """
    Subclass of ``django.forms.ModelForm`` which contains the math fields
    Inherit this class in your forms to add math captcha support::
    
        class MyForm(MathCaptchaModelForm):
            field1 = forms.fields.CharField()
            # ...
            
            class Meta:
                model = MyModel
            
    """
    math_captcha_field = MathField(label=settings.QUESTION)
    math_captcha_question = forms.fields.CharField(widget=NullWidget())

    def clean(self):
        super(MathCaptchaModelForm, self).clean()
        math_clean(self)
        
class MathCaptchaForm(forms.Form):
    """
    Subclass of ``django.forms.Form`` which contains the math fields.
    Inherit this class in your forms to add math captcha support::
    
        class MyForm(MathCaptchaForm):
            field1 = forms.fields.CharField()
            # ...
            
    """
    math_captcha_field = MathField(label=settings.QUESTION)
    math_captcha_question = forms.fields.CharField(widget=NullWidget())

    def clean(self):
        super(MathCaptchaForm, self).clean()
        math_clean(self)    
