from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class PortalUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Portal", {"fields": ("role", "customer", "is_enabled")}),
    )
    list_display = ("username", "email", "role", "customer", "is_enabled", "is_staff")

# Register your models here.
