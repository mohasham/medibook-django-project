from django.contrib import admin

# Register your models here.
# Django's admin tools. A new model is invisible in /admin/ until it is registered.
from django.contrib import admin

# The two models from doctors/models.py (the dot means "this same app").
from .models import Doctor, Specialty


# Registers Specialty so it appears in /admin/.
@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    # Columns in the list table. The trailing comma makes it a tuple.
    list_display = ("name",)
    # Search box above the list.
    search_fields = ("name",)


# Registers Doctor so it appears in /admin/.
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    # "__str__" shows "Dr. First Last"; is_active adds a green/red icon column.
    list_display = ("__str__", "is_active")
    # Filter sidebar on the right.
    list_filter = ("is_active", "specialties")
    # Double underscore follows the link to the user and searches their name.
    search_fields = ("user__username", "user__first_name", "user__last_name")
    # Two-box picker instead of the Ctrl+click multi-select.
    filter_horizontal = ("specialties",)