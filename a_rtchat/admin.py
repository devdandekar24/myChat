from django.contrib import admin
from .models import *

class GroupMessageAdmin(admin.ModelAdmin):
    readonly_fields = ['body','file','author']

admin.site.register(ChatGroup)
admin.site.register(GroupMessage,GroupMessageAdmin)