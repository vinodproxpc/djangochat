from django.contrib import admin
from .models import Message, UserChannel

class MessageAdmin(admin.ModelAdmin):
    list_display  = ["from_who","to_who","message","date","time","has_been_seen"]

admin.site.register(Message,MessageAdmin)

class UserChannelAdmin(admin.ModelAdmin):
    list_display  = ["user","channel_name"]

admin.site.register(UserChannel,UserChannelAdmin)
