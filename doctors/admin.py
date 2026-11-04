from django.contrib import admin

from .models import Availability, Doctor, Specialty


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class AvailabilityInline(admin.TabularInline):
    # Shows the doctor's working hours as rows inside the Doctor page.
    model = Availability
    extra = 1


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("__str__", "is_active")
    list_filter = ("is_active", "specialties")
    search_fields = ("user__username", "user__first_name", "user__last_name")
    filter_horizontal = ("specialties",)
    inlines = [AvailabilityInline]