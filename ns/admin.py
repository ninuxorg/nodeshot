from django.contrib import admin
from ns.models import * 

class NodeAdmin(admin.ModelAdmin):
    list_display  = ('name', 'owner', 'status', 'added', 'updated')
    list_filter   = ('status', 'added', 'updated')
    search_fields = ('name', 'owner', 'email', 'cap')
    save_on_top = True
admin.site.register(Node, NodeAdmin)

admin.site.register(Interface)
admin.site.register(HNAv4)
admin.site.register(Link)
admin.site.register(Device)