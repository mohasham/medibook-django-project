from django.shortcuts import render

# Create your views here.
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Doctor, Specialty
from .slots import available_slots


@login_required
def doctor_list(request):
    doctors = Doctor.objects.filter(is_active=True).select_related("user")
    # Optional filter, e.g. /doctors/?specialty=3
    specialty_id = request.GET.get("specialty")
    if specialty_id:
        doctors = doctors.filter(specialties__id=specialty_id)
    return render(request, "doctors/doctor_list.html", {
        "doctors": doctors.distinct(),
        "specialties": Specialty.objects.all(),
        "selected": specialty_id,
    })


@login_required
def doctor_detail(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk, is_active=True)
    # Open slots for the next 7 days, grouped by day. Booked times are
    # already removed by available_slots.
    days = []
    for i in range(7):
        day = date.today() + timedelta(days=i)
        slots = available_slots(doctor, day)
        if slots:
            days.append({"day": day, "slots": slots})
    return render(request, "doctors/doctor_detail.html", {
        "doctor": doctor,
        "days": days,
    })