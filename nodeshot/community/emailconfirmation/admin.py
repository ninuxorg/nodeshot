from django.contrib import admin

from .models import EmailAddress, EmailConfirmation


class EmailAddressAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'verified', 'primary')

class EmailConfirmationAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'key_expired')

admin.site.register((EmailAddress,), EmailAddressAdmin)
admin.site.register((EmailConfirmation,), EmailConfirmationAdmin)
