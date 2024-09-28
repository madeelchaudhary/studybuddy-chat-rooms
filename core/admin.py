from django.contrib import admin

from core.models import User

# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ['username', 'first_name', 'last_name']

    list_display = ['username', 'first_name',
                    'last_name', 'is_active', 'is_staff', 'last_login']
    list_filter = ['is_active', 'is_staff']
