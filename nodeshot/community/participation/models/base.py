from django.db import models


class UpdateCountsMixin(models.Model):
    """
    Updates node_rating_count record each time an
    Instance of an extended model is created or deleted
    """

    class Meta:
        abstract = True

    def update_count(self):
        """ this method needs to be overwritten """
        pass

    def save(self, *args, **kwargs):
        """ custom save method to update counts """
        # the following lines determines if the comment is being created or not
        # in case the comment exists the pk attribute is an int
        created = type(self.pk) is not int

        super(UpdateCountsMixin, self).save(*args, **kwargs)

        # this operation must be performed after the parent save
        if created:
            self.update_count()

    def delete(self, *args, **kwargs):
        """ custom delete method to update counts """
        super(UpdateCountsMixin, self).delete(*args, **kwargs)
        self.update_count()
