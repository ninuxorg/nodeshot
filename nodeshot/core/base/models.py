from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import utc
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
    """
    access_level = models.CharField(_('access level'), max_length=10, choices=ACCESS_LEVELS, default=ACCESS_LEVELS[0][0])
    
    class Meta:
        abstract = True

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
        super(OrderedModel, self).save()

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