from django.contrib import admin

from chatrooms.models import Room

# Register your models here.


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'host']
    search_fields = ['name']
    list_filter = ['topic', 'host']
