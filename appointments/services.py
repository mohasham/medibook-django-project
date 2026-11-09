from datetime import timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone

from doctors.models import Doctor
from doctors.slots import generate_slots

from .models import CHANGE_DEADLINE_HOURS, Appointment


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


def _check_can_change(appointment, user):
    """Shared rules for cancelling and rescheduling. Raises BookingError."""
    # Only the appointment's own patient may change it.
    if appointment.patient_id != user.id:
        raise BookingError("You can only change your own appointments.")

    # Finished or already-cancelled appointments are frozen.
    if appointment.status not in (
        Appointment.Status.PENDING,
        Appointment.Status.CONFIRMED,
    ):
        raise BookingError("This appointment can no longer be changed.")

    # Too close to the start time (the 2-hour rule).
    deadline = appointment.start_time - timedelta(hours=CHANGE_DEADLINE_HOURS)
    if timezone.now() > deadline:
        raise BookingError(
            f"Appointments cannot be changed within {CHANGE_DEADLINE_HOURS} hours of the start time."
        )


def cancel_appointment(appointment_id, user):
    """Cancel an appointment, enforcing the rules above."""
    with transaction.atomic():
        # Lock this row so a cancel and a reschedule can't run at the same time.
        appointment = Appointment.objects.select_for_update().get(pk=appointment_id)
        _check_can_change(appointment, user)
        appointment.status = Appointment.Status.CANCELLED
        appointment.save(update_fields=["status"])
        return appointment


def reschedule_appointment(appointment_id, user, new_start_time):
    """Move an appointment to a new slot with the same doctor.

    Implemented as: book the new slot, then cancel the old one, inside one
    transaction. If the new slot is taken, nothing changes.
    """
    with transaction.atomic():
        old = Appointment.objects.select_for_update().get(pk=appointment_id)
        _check_can_change(old, user)

        if new_start_time == old.start_time:
            raise BookingError("That is already your appointment time.")

        # Reuses all the booking checks and the doctor row lock.
        new = book_appointment(old.doctor_id, user, new_start_time)

        old.status = Appointment.Status.CANCELLED
        old.save(update_fields=["status"])
        return new