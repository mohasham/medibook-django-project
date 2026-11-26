from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from accounts.models import User

from .services import BookingError, book_appointment


@login_required
@require_POST
def book(request, doctor_id):
    # Only patients book. Doctors and admins are turned away.
    if request.user.role != User.Role.PATIENT:
        messages.error(request, "Only patients can book appointments.")
        return redirect("doctors:detail", pk=doctor_id)

    try:
        # The button's value is ISO text such as 2026-11-25T14:00:00+02:00.
        start = datetime.fromisoformat(request.POST["start_time"])
        book_appointment(doctor_id, request.user, start)
        messages.success(request, "Appointment booked.")
    except BookingError as e:
        messages.error(request, str(e))
    except (KeyError, ValueError):
        messages.error(request, "Invalid time.")

    return redirect("doctors:detail", pk=doctor_id)