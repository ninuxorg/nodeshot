from django.contrib import admin

class BaseAdmin(admin.ModelAdmin):
    """
    Abstract administration model for BaseDate models.
        * 'added' and 'updated' fields readonly
        * save-on-top button enabled by default
    """
    save_on_top = True
    readonly_fields = ['added', 'updated']

#class BaseAccessLevelAdmin(admin.ModelAdmin):
#    """
#    excludes private
#    """
#    def queryset(self, request):
#        q = super(BaseAccessLevelAdmin, self).queryset(request)
#        return q.not_private()

class BaseStackedInline(admin.StackedInline):
    readonly_fields = ['added', 'updated']
    extra = 0

class BaseTabularInline(admin.TabularInline):
    readonly_fields = ['added', 'updated']
    extra = 0