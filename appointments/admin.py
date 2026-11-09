from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("doctor", "patient", "start_time", "status")
    list_filter = ("status", "doctor")
    date_hierarchy = "start_time"