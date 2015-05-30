from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from .settings import ACL_DEFAULT_VALUE, ACL_DEFAULT_EDITABLE
from .choices import ACCESS_LEVELS
from .utils import choicify, now


class BaseShortcut(models.Model):
    """
    Abstract Model providing shortcuts to main manager methods
    Handy for shell prototyping
    """
    
    class Meta:
        abstract = True
        
    @classmethod
    def all(cls):
        return cls.objects.all()
    
    @classmethod
    def filter(cls, *args, **kwargs):
        return cls.objects.filter(*args, **kwargs)
    
    @classmethod
    def exclude(cls, *args, **kwargs):
        return cls.objects.exclude(*args, **kwargs)
    
    @classmethod
    def count(cls, *args, **kwargs):
        return cls.objects.count(*args, **kwargs)
    
    # --- custom methods, copying Rails :) --- #
    
    @classmethod
    def last(cls):
        return cls.objects.last()
    
    @classmethod
    def first(cls):
        return cls.objects.first()
    
    @classmethod
    def find(cls, pk):
        return cls.objects.find(pk)


class BaseDate(BaseShortcut):
    """
    Base Abstract Model that provides:
        * an added field that automatically sets the insert date
        * an updated field which updates itself automatically
    We don't use django's autoaddnow=True because that makes the fields not visible in the admin.
    """
    added = models.DateTimeField(_('created on'), default=now())
    updated = models.DateTimeField(_('updated on'), default=now())

    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        """
        automatically update updated date field
        """
        # auto fill updated field with current time unless explicitly disabled
        auto_update = kwargs.get('auto_update', True)
        if auto_update:
            self.updated = now()
        
        # remove eventual auto_update
        if 'auto_update' in kwargs:
            kwargs.pop('auto_update')
        
        super(BaseDate, self).save(*args, **kwargs)


class BaseAccessLevel(BaseDate):
    """
    Base Abstract Model that extends BaseDate and provides
    an additional field for access level management.
    The field default and editable attributes value can be
    overriden by adding some directives in the settings file.
    
    DEFAULT VALUE
        To edit the default value for the access_level field of a certain
        model you will have to add the following setting in your settings.py file:
    
        NODESHOT_ACL_{APP_NAME}_{MODEL_NAME}_DEFAULT = 'public'
    
        where {APP_NAME} is the uppercase name of an app like "NODES"
        and {MODEL_NAME} is the uppercase name of a model like "NODE"
        The values will have to be one of the possible values specified in
        "nodeshot.core.base.choices.ACCESS_LEVELS"
        The possible values are public or the id of the group saved in the database
        (default ones are 1 for registered, 2 for community and 3 for trusted)
        
        For the cases in which no setting is specified the fallback setting
        NODESHOT_ACL_DEFAULT_VALUE will be used.
    
    EDITABLE
        If you want to disable the possibility to edit the access_level field
        for a given model you will have to add the following settings in the settings.py file:
        
        NODESHOT_ACL_{APP_NAME}_{MODEL_NAME}_EDITABLE = False
        
        where {APP_NAME} is the uppercase name of an app like "NODES"
        and {MODEL_NAME} is the uppercase name of a model like "NODE"
        
        For the cases in which no setting is specified the fallback setting
        NODESHOT_ACL_DEFAULT_EDITABLE will be used.
    
    """
    access_level = models.SmallIntegerField(_('access level'), choices=choicify(ACCESS_LEVELS), default=ACCESS_LEVELS.get(ACL_DEFAULT_VALUE))
    
    class Meta:
        abstract = True
    
    def __init__(self, *args, **kwargs):
        """
        Determines default value for field "access_level" and determines if is editable
        In the case the field is not editable it won't show up at all
        """
        
        # {APP_NAME}_{MODEL_NAME}, eg: NODES_NODE
        app_descriptor = '%s_%s' % (self._meta.app_label.upper(), self._meta.object_name.upper())
        
        # looks up in settings.py
        # example: NODESHOT_ACL_NODES_NODE_DEFAULT
        # defaults to NODESHOT_ACL_DEFAULT_VALUE
        value = getattr(settings, 'NODESHOT_ACL_%s_DEFAULT' % app_descriptor, ACL_DEFAULT_VALUE)
        ACL_DEFAULT = ACCESS_LEVELS.get(value)
        
        # looks up in settings.py
        # example: NODESHOT_ACL_NODES_NODE_EDITABLE
        ACL_EDITABLE = getattr(settings, 'NODESHOT_ACL_%s_EDITABLE' % app_descriptor, ACL_DEFAULT_EDITABLE)
        
        # set "default" and "editable" attributes
        self._meta.get_field('access_level').default = ACL_DEFAULT
        self._meta.get_field('access_level').editable = ACL_EDITABLE
        
        # call super __init__
        super(BaseAccessLevel, self).__init__(*args, **kwargs)


class BaseOrdered(models.Model):
    """
    Ordered Model provides functions for ordering objects in the Django Admin
    """
    order = models.PositiveIntegerField(blank=True, help_text=_('Leave blank to set as last'))

    class Meta:
        ordering = ["order"]
        abstract = True
    
    def get_auto_order_queryset(self):
        return self.__class__.objects.all()
    
    def save(self, *args, **kwargs):
        """ if order left blank """
        if self.order == '' or self.order is None:
            try:
                self.order = self.get_auto_order_queryset().order_by("-order")[0].order + 1
            except IndexError:
                self.order = 0
        super(BaseOrdered, self).save()


class BaseOrderedACL(BaseOrdered, BaseAccessLevel):
    
    class Meta:
        ordering = ["order"]
        abstract = True
