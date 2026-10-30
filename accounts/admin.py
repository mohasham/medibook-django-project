from django.contrib import admin
# Django's built-in admin screen for users. It already handles password hashing
# and the "add user" form properly, so we extend it instead of writing our own.
from django.contrib.auth.admin import UserAdmin

from .models import User


# This decorator registers the model with the admin site (same as admin.site.register).
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # fieldsets controls the layout of the EDIT user page.
    # We keep all the default sections and append one new "Role" section
    # containing our two extra fields.
    fieldsets = UserAdmin.fieldsets + (("Role", {"fields": ("role", "phone")}),)

    # add_fieldsets controls the layout of the CREATE user page (a separate form),
    # so the new fields must be added here too, or they'd be missing on creation.
    add_fieldsets = UserAdmin.add_fieldsets + (("Role", {"fields": ("role", "phone")}),)

    # Columns shown in the users list table.
    list_display = ("username", "email", "role", "is_staff")

    # Adds a filter sidebar on the right of the list (e.g. show only doctors).
    list_filter = ("role", "is_staff")