from django.contrib import admin
from django.utils.html import format_html

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
    # "photo_thumb" is the method below; it shows a small round photo.
    list_display = ("photo_thumb", "__str__", "is_active")
    # Clicking the name (not the photo) opens the doctor.
    list_display_links = ("__str__",)
    list_filter = ("is_active", "specialties")
    search_fields = ("user__username", "user__first_name", "user__last_name")
    filter_horizontal = ("specialties",)
    inlines = [AvailabilityInline]

    @admin.display(description="Photo")
    def photo_thumb(self, obj):
        if obj.photo:
            # format_html escapes the URL safely before putting it in HTML.
            return format_html(
                '<img src="{}" width="40" height="40" '
                'style="border-radius:50%;object-fit:cover">',
                obj.photo.url,
            )
        return "-"