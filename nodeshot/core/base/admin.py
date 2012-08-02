from django.contrib import admin

class BaseAdmin(admin.ModelAdmin):
    """
    Abstract administration model for BaseDate models.
        * 'added' and 'updated' fields readonly
        * save-on-top button enabled by default
    """
    save_on_top = True
    readonly_fields = ['added', 'updated']

    #class Meta:
    #    abstract = True

class BaseStackedInline(admin.StackedInline):
    readonly_fields = ('added', 'updated')
    extra = 0