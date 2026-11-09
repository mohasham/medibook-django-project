from django.db import IntegrityError, transaction
from django.utils import timezone

from doctors.models import Doctor
from doctors.slots import generate_slots

from .models import Appointment


class BookingError(Exception):
    """Raised when a booking cannot be made. The message is safe to show users."""


def book_appointment(doctor_id, patient, start_time):
    """Book `start_time` with a doctor for `patient`, safely under concurrency."""
    with transaction.atomic():
        # Lock the doctor's row until this transaction ends. A second
        # simultaneous booking for the same doctor waits here, so the
        # checks below cannot be raced.
        # (SQLite ignores row locks, PostgreSQL enforces them. The unique
        # constraint below protects us on both.)
        doctor = Doctor.objects.select_for_update().get(pk=doctor_id, is_active=True)

        if start_time <= timezone.now():
            raise BookingError("You cannot book a time in the past.")

        # The time must be one of the doctor's real slots.
        valid = generate_slots(doctor, timezone.localtime(start_time).date())
        if start_time not in valid:
            raise BookingError("That time is not an available slot.")

        # Already taken by an active appointment?
        taken = Appointment.objects.filter(
            doctor=doctor, start_time=start_time
        ).exclude(status=Appointment.Status.CANCELLED)
        if taken.exists():
            raise BookingError("Sorry, that slot was just booked.")

        try:
            return Appointment.objects.create(
                doctor=doctor, patient=patient, start_time=start_time
            )
        except IntegrityError:
            # The database constraint is the last line of defense.
            raise BookingError("Sorry, that slot was just booked.")