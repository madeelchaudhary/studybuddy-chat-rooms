from django.contrib import admin

from chatrooms.models import Message, Room, Topic

# Register your models here.


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'host']
    search_fields = ['name']
    list_filter = ['topic', 'host']


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_filter = ['user', 'room']
    sortable_by = ["created_at"]

    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['user', 'room']
