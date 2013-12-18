from django.utils.translation import ugettext_lazy as _


class Attribute:
    """ Open311 Service Definition Attribute """
    def __init__(self,*args,**kwargs):
        self.code = kwargs['code']
        self.description = kwargs['description']
        self.datatype = kwargs['datatype']
        self.datatype_description = kwargs['datatype_description']
        self.order = kwargs['order']
        self.values= kwargs.get('values', None)
        self.required= kwargs.get('required', False)


SERVICES = {
    'node': {
        'name': _('Node insertion'),
        'description': _('Insert new nodes'),
        'keywords': '',
        'group': ''
    },
    'vote': {
        'name': _('Vote'),
        'description': _('Like or Dislike something'),
        'keywords': '',
        'group': ''
    },
    'comment': {
        'name': _('Comment'),
        'description': _('Leave a comment'),
        'keywords': '',
        'group': ''
    },
    'rating': {
        'name': _('Rate'),
        'description': _('Leave your rating about something'),
        'keywords': '',
        'group': ''
    }
}