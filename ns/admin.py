from django.contrib import admin
from ns.models import * 

admin.site.register(Node)
admin.site.register(Interface)
admin.site.register(HNAv4)
admin.site.register(Link)
admin.site.register(Device)
admin.site.register(DeviceType)
