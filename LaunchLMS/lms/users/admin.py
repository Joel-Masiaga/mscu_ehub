from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile

# Extend the default Django UserAdmin to support the custom User model
class UserAdmin(BaseUserAdmin):
    ordering = ['email']
    list_display = ['email', 'role', 'is_staff', 'is_active', 'is_superuser']
    list_filter = ['role', 'is_staff', 'is_superuser']
    search_fields = ['email']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )

# Register the custom User model and Profile
admin.site.register(User, UserAdmin)
admin.site.register(Profile)
