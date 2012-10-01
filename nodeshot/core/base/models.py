from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import utc
from django.conf import settings
from datetime import datetime
from nodeshot.core.base.choices import ACCESS_LEVELS

class BaseDate(models.Model):
    """
    Base Abstract Model that provides:
        * an added field that automatically sets the insert date
        * an updated field which updates itself automatically
    We don't use django's autoaddnow=True because that makes the fields not visible in the admin.
    """
    added = models.DateTimeField(_('created on'), default=datetime.utcnow().replace(tzinfo=utc))
    updated = models.DateTimeField(_('updated on'), default=datetime.utcnow().replace(tzinfo=utc))

    def save(self, *args, **kwargs):
        """
        automatically update updated date field
        """
        self.updated = datetime.utcnow().replace(tzinfo=utc)
        super(BaseDate, self).save(*args, **kwargs)

    class Meta:
        abstract = True

class BaseAccessLevel(BaseDate):
    """
    Base Abstract Model that extends BaseDate and provides an additional field for access level management.
    The field default and editable attributes value can be overriden by adding some directives in the settings file.
    
    DEFAULT VALUE
        To edit the default value for the access_level field of a certain model you will have to add the following setting in the settings.py file:
    
        NODESHOT['DEFAULTS']['ACL_{APP_NAME}_{MODEL_NAME}'] = 'public'
    
        where {APP_NAME} is the uppercase name of an app like "nodes" or "network"
        and {MODEL_NAME} is the uppercase name of a model like "Node" or "Device"
        The values will have to be one of the possible values specified in "nodeshot.core.base.choices.ACCESS_LEVELS"
        The possible values are public, private or the id of the group saved in the database (default ones are 1 for registered and 2 for community)
        
        For the cases in which no setting is specified the fallback setting NODESHOT['DEFAULTS']['ACL_GLOBAL'] will be used.
    
    EDITABLE
        If you want to disable the possibility to edit the access_level field for a given model you will have to add the following settings in the settings.py file:
        
        NODESHOT['DEFAULTS']['ACL_{APP_NAME}_{MODEL_NAME}_EDITABLE'] = False
        
        where {APP_NAME} is the uppercase name of an app like "nodes" or "network"
        and {MODEL_NAME} is the uppercase name of a model like "Node" or "Device"
        
        For the cases in which no setting is specified the fallback setting NODESHOT['DEFAULTS']['ACL_GLOBAL_EDITABLE'] will be used.
    
    """
    access_level = models.CharField(_('access level'), max_length=10, choices=ACCESS_LEVELS, default=ACCESS_LEVELS[0][0])
    
    class Meta:
        abstract = True
    
    def __init__(self, *args, **kwargs):
        """
        Determines default value for field "access_level" and determines if is editable
        In the case the field is not editable it won't show up at all
        """
        
        # {APP_NAME}_{MODEL_NAME}, eg: NODES_NODE, SERVICES_SERVICE, NETWORK_IP
        app_descriptor = '%s_%s' % (self._meta.app_label.upper(), self._meta.object_name.upper())
        
        try:
            # looks up in settings.py
            # example NODESHOT['DEFAULTS']['ACL_NETWORK_NODE']
            ACL_DEFAULT = settings.NODESHOT['DEFAULTS']['ACL_%s' % app_descriptor]
        except KeyError:
            # if setting is not found use the global setting 
            ACL_DEFAULT = settings.NODESHOT['DEFAULTS']['ACL_GLOBAL']
        
        try:
            # looks up in settings.py
            # example NODESHOT['SETTINGS']['ACL_NETWORK_NODE_EDITABLE']
            ACL_EDITABLE = settings.NODESHOT['SETTINGS']['ACL_%s_EDITABLE' % app_descriptor]
        except KeyError:
            # if setting is not found use the global setting 
            ACL_EDITABLE = settings.NODESHOT['SETTINGS']['ACL_GLOBAL_EDITABLE']
        
        # set "default" and "editable" attributes
        self._meta.get_field('access_level').default = ACL_DEFAULT
        self._meta.get_field('access_level').editable = ACL_EDITABLE
        
        # call super __init__
        super(BaseAccessLevel, self).__init__(*args, **kwargs)

class BaseOrdered(BaseAccessLevel):
    """
    Ordered Model provides functions for ordering objects in the Django Admin
    """
    order = models.PositiveIntegerField(blank=True, help_text=_('Leave blank to set as last'))

    class Meta:
        ordering = ["order"]
        abstract = True
        
    def save(self):
        if not self.id:
            try:
                self.order = self.__class__.objects.all().order_by("-order")[0].order + 1
            except IndexError:
                self.order = 1
        super(BaseOrdered, self).save()

    def order_link(self):
        """
        Shows move-up and move-down links in the django admin
        """
        model_type_id = ContentType.objects.get_for_model(self.__class__).id
        model_id = self.id
        kwargs = {"direction": "up", "model_type_id": model_type_id, "model_id": model_id}
        from django.core.urlresolvers import reverse
        url_up = reverse("admin-move", kwargs=kwargs)
        kwargs["direction"] = "down"
        url_down = reverse("admin-move", kwargs=kwargs)
        return '<a href="%s" class="up"><b>up</b><span>&nbsp;</span></a> <a href="%s" class="down"><b>down</b><span>&nbsp;</span></a>' % (url_up, url_down)
    order_link.allow_tags = True
    order_link.short_description = 'Move'
    order_link.admin_order_field = 'order'

    @staticmethod
    def move_up(model_type_id, model_id):
        """
        Changes the order of two items so that the one with the lower order goes up
        """
        try:
            ModelClass = ContentType.objects.get(id=model_type_id).model_class()
            lower_model = ModelClass.objects.get(id=model_id)
            higher_model = ModelClass.objects.filter(order__gt=lower_model.order).order_by('order')[0]
            lower_model.order, higher_model.order = higher_model.order, lower_model.order
            higher_model.save()
            lower_model.save()
        except IndexError:
            pass
        except ModelClass.DoesNotExist:
            pass

    @staticmethod
    def move_down(model_type_id, model_id):
        """
        Changes the order of two items so that the one with the higher order goes down
        """
        try:
            ModelClass = ContentType.objects.get(id=model_type_id).model_class()
            higher_model = ModelClass.objects.get(id=model_id)
            lower_model = ModelClass.objects.filter(order__lt=higher_model.order)[0]
            lower_model.order, higher_model.order = higher_model.order, lower_model.order
            higher_model.save()
            lower_model.save()
        except IndexError:
            pass
        except ModelClass.DoesNotExist:
            pass