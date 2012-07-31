from django.contrib import admin

class BaseAdmin(admin.ModelAdmin):
    """
    Abstract administration model for BaseDate models.
        * 'added' and 'updated' fields are everytime readonly
        * save on top button is everytime present
    """
    save_on_top = True
    readonly_fields = ['added', 'updated']

    class Meta:
        abstract = True
