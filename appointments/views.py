from datetime import date, datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import User
from doctors.slots import available_slots

from .models import Appointment
from .services import (
    BookingError,
    book_appointment,
    cancel_appointment,
    reschedule_appointment,
)


@login_required
@require_POST
def book(request, doctor_id):
    # Only patients book. Doctors and admins are turned away.
    if request.user.role != User.Role.PATIENT:
        messages.error(request, "Only patients can book appointments.")
        return redirect("doctors:detail", pk=doctor_id)

    try:
        # The button's value is ISO text such as 2026-11-30T09:00:00+02:00.
        start = datetime.fromisoformat(request.POST["start_time"])
        book_appointment(doctor_id, request.user, start)
        messages.success(request, "Appointment booked.")
        return redirect("appointments:mine")  # show the new booking
    except BookingError as e:
        messages.error(request, str(e))
    except (KeyError, ValueError):
        messages.error(request, "Invalid time.")

    return redirect("doctors:detail", pk=doctor_id)


@login_required
def my_appointments(request):
    # Only the logged-in patient's own appointments, newest first.
    appointments = (
        Appointment.objects.filter(patient=request.user)
        .select_related("doctor__user")
        .order_by("-start_time")
    )
    return render(request, "appointments/my_appointments.html", {
        "appointments": appointments,
        "now": timezone.now(),  # used to hide buttons on past appointments
    })


@login_required
@require_POST
def cancel(request, pk):
    # 404 if it does not exist or belongs to someone else.
    get_object_or_404(Appointment, pk=pk, patient=request.user)
    try:
        # The service enforces the 2-hour rule and the status rules.
        cancel_appointment(pk, request.user)
        messages.success(request, "Appointment cancelled.")
    except BookingError as e:
        messages.error(request, str(e))
    return redirect("appointments:mine")


@login_required
def reschedule(request, pk):
    appt = get_object_or_404(Appointment, pk=pk, patient=request.user)

    if request.method == "POST":
        try:
            new_start = datetime.fromisoformat(request.POST["start_time"])
            # Books the new slot and cancels the old one in one transaction.
            reschedule_appointment(pk, request.user, new_start)
            messages.success(request, "Appointment rescheduled.")
            return redirect("appointments:mine")
        except BookingError as e:
            messages.error(request, str(e))
        except (KeyError, ValueError):
            messages.error(request, "Invalid time.")
        return redirect("appointments:reschedule", pk=pk)

    # GET: show the same doctor's free slots for the next 7 days.
    days = []
    for i in range(7):
        day = date.today() + timedelta(days=i)
        slots = available_slots(appt.doctor, day)
        if slots:
            days.append({"day": day, "slots": slots})
    return render(request, "appointments/reschedule.html", {"appt": appt, "days": days})