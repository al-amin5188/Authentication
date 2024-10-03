from django.contrib import admin
from authuser.models import PasswordResetTable

# Register your models here.

class PasswordResetTableAdmin(admin.ModelAdmin):
    list_display=('user','reset_id','created_time')
    

admin.site.register(PasswordResetTable, PasswordResetTableAdmin)