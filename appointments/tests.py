from datetime import date, datetime, time, timedelta

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from accounts.models import User
from doctors.models import Availability, Doctor
from doctors.slots import available_slots

from .models import Appointment
from .services import (
    BookingError,
    book_appointment,
    cancel_appointment,
    reschedule_appointment,
)


def next_monday():
    today = date.today()
    return today + timedelta(days=(7 - today.weekday()) % 7 or 7)


class BookingTests(TestCase):
    def setUp(self):
        # Django creates a fresh empty test database, so we build our own data.
        doctor_user = User.objects.create_user("doc", password="x", role="doctor")
        self.doctor = Doctor.objects.create(user=doctor_user)
        Availability.objects.create(
            doctor=self.doctor, weekday=0,
            start_time=time(9, 0), end_time=time(12, 0), slot_minutes=30,
        )
        self.p1 = User.objects.create_user("p1", password="x")
        self.p2 = User.objects.create_user("p2", password="x")
        self.slot = timezone.make_aware(datetime.combine(next_monday(), time(9, 0)))

    def test_booking_works(self):
        appt = book_appointment(self.doctor.id, self.p1, self.slot)
        self.assertEqual(appt.status, Appointment.Status.CONFIRMED)

    def test_double_booking_is_blocked(self):
        book_appointment(self.doctor.id, self.p1, self.slot)
        with self.assertRaises(BookingError):
            book_appointment(self.doctor.id, self.p2, self.slot)
        self.assertEqual(Appointment.objects.count(), 1)

    def test_database_constraint_blocks_duplicates(self):
        Appointment.objects.create(doctor=self.doctor, patient=self.p1, start_time=self.slot)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Appointment.objects.create(doctor=self.doctor, patient=self.p2, start_time=self.slot)

    def test_cancelled_slot_can_be_rebooked(self):
        appt = book_appointment(self.doctor.id, self.p1, self.slot)
        appt.status = Appointment.Status.CANCELLED
        appt.save()
        book_appointment(self.doctor.id, self.p2, self.slot)
        self.assertEqual(Appointment.objects.count(), 2)

    def test_past_time_rejected(self):
        past = timezone.now() - timedelta(days=1)
        with self.assertRaises(BookingError):
            book_appointment(self.doctor.id, self.p1, past)

    def test_time_outside_availability_rejected(self):
        odd = self.slot + timedelta(minutes=10)  # 09:10 is not a real slot
        with self.assertRaises(BookingError):
            book_appointment(self.doctor.id, self.p1, odd)

    def test_booked_slot_hidden_from_available_slots(self):
        day = next_monday()
        self.assertIn(self.slot, available_slots(self.doctor, day))
        book_appointment(self.doctor.id, self.p1, self.slot)
        self.assertNotIn(self.slot, available_slots(self.doctor, day))


class CancelRescheduleTests(TestCase):
    def setUp(self):
        doctor_user = User.objects.create_user("doc", password="x", role="doctor")
        self.doctor = Doctor.objects.create(user=doctor_user)
        Availability.objects.create(
            doctor=self.doctor, weekday=0,
            start_time=time(9, 0), end_time=time(12, 0), slot_minutes=30,
        )
        self.p1 = User.objects.create_user("p1", password="x")
        self.p2 = User.objects.create_user("p2", password="x")
        day = next_monday()
        self.slot = timezone.make_aware(datetime.combine(day, time(9, 0)))
        self.slot2 = timezone.make_aware(datetime.combine(day, time(10, 0)))
        self.appt = book_appointment(self.doctor.id, self.p1, self.slot)

    def test_cancel_works(self):
        cancel_appointment(self.appt.id, self.p1)
        self.appt.refresh_from_db()
        self.assertEqual(self.appt.status, Appointment.Status.CANCELLED)

    def test_cannot_cancel_someone_elses(self):
        with self.assertRaises(BookingError):
            cancel_appointment(self.appt.id, self.p2)

    def test_cannot_cancel_within_deadline(self):
        # Pretend the appointment starts in 1 hour.
        Appointment.objects.filter(pk=self.appt.pk).update(
            start_time=timezone.now() + timedelta(hours=1)
        )
        with self.assertRaises(BookingError):
            cancel_appointment(self.appt.id, self.p1)

    def test_cannot_cancel_twice(self):
        cancel_appointment(self.appt.id, self.p1)
        with self.assertRaises(BookingError):
            cancel_appointment(self.appt.id, self.p1)

    def test_reschedule_works(self):
        new = reschedule_appointment(self.appt.id, self.p1, self.slot2)
        self.appt.refresh_from_db()
        self.assertEqual(self.appt.status, Appointment.Status.CANCELLED)
        self.assertEqual(new.start_time, self.slot2)
        self.assertEqual(new.status, Appointment.Status.CONFIRMED)

    def test_reschedule_to_taken_slot_changes_nothing(self):
        book_appointment(self.doctor.id, self.p2, self.slot2)
        with self.assertRaises(BookingError):
            reschedule_appointment(self.appt.id, self.p1, self.slot2)
        self.appt.refresh_from_db()
        self.assertEqual(self.appt.status, Appointment.Status.CONFIRMED)