from datetime import datetime, timedelta

from django.utils import timezone


def generate_slots(doctor, day):
    """Return timezone-aware start datetimes for `doctor` on `day`
    (a datetime.date), built from the doctor's weekly Availability rows.
    Slots that have already passed are left out.
    """
    slots = []
    now = timezone.now()

    # Only the blocks for this weekday (Monday = 0 ... Sunday = 6).
    blocks = doctor.availabilities.filter(weekday=day.weekday())

    for block in blocks:
        step = timedelta(minutes=block.slot_minutes)

        # Combine the date with the block's times into real datetimes.
        current = timezone.make_aware(datetime.combine(day, block.start_time))
        end = timezone.make_aware(datetime.combine(day, block.end_time))

        # A slot is valid only if it fits fully before the block ends.
        while current + step <= end:
            if current > now:
                slots.append(current)
            current += step

    return slots

def available_slots(doctor, day):
    """Like generate_slots, but without times that already have an active
    (non-cancelled) appointment. This is what patients should see."""
    # Imported here to avoid a circular import between the two apps.
    from appointments.models import Appointment

    slots = generate_slots(doctor, day)
    if not slots:
        return []

    booked = set(
        Appointment.objects.filter(
            doctor=doctor,
            start_time__gte=min(slots),
            start_time__lte=max(slots),
        )
        .exclude(status=Appointment.Status.CANCELLED)
        .values_list("start_time", flat=True)
    )
    return [s for s in slots if s not in booked]