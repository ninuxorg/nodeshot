from django.utils.translation import ugettext_lazy as _
from nodeshot.core.base.utils import choicify


SEX = {
    'male': 'M',
    'female': 'F'
}
SEX_CHOICES = choicify(SEX)