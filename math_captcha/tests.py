from django.test.testcases import TestCase
from forms import MathCaptchaForm
from util import encode

class MathCaptchaTest(TestCase):
    def test_unbound(self):
        form = MathCaptchaForm()
        self.assert_(form.as_p().endswith('<input type="text" name="math_captcha_field" id="id_math_captcha_field" /></p>'))
        
    def test_bad_operation(self):
        form = MathCaptchaForm({'math_captcha_field':'0', 'math_captcha_question':encode(' - 1')})
        self.assert_(form.as_p().find('errorlist') > -1)

    def test_success(self):
        form = MathCaptchaForm({'math_captcha_field':'0', 'math_captcha_question':encode('1 - 1')})        
        self.assert_(form.as_p().find('errorlist') == -1)

    def test_wrong_value(self):
        form = MathCaptchaForm({'math_captcha_field':'1', 'math_captcha_question':encode('1 - 1')})        
        self.assert_(form.as_p().find('errorlist') > -1)
        
    def test_negative_value(self):
        form = MathCaptchaForm({'math_captcha_field':'-1', 'math_captcha_question':encode('0 - 1')})
        self.assert_(form.as_p().find('errorlist') > -1)
        
