from django.contrib import admin

from chatrooms.models import Room, Topic

# Register your models here.


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'host']
    search_fields = ['name']
    list_filter = ['topic', 'host']


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    search_fields = ['name']
