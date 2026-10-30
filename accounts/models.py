# AbstractUser is Django's full built-in user (username, password, email,
# first/last name, is_staff, is_active, permissions...). We inherit from it so
# login, admin, and permissions keep working, and add only what we need.
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # Role is a nested class holding the allowed values.
    # TextChoices gives each choice two parts: (value stored in DB, label shown to humans).
    #   PATIENT = "patient"  -> the DB stores "patient"
    #   "Patient"            -> the admin/forms display "Patient"
    class Role(models.TextChoices):
        PATIENT = "patient", "Patient"
        DOCTOR = "doctor", "Doctor"
        ADMIN = "admin", "Admin"

    # The field that decides what a user can do inside OUR app.
    # - max_length=10: long enough for "patient" (7 chars), the longest value.
    # - choices: Django validates against the Role list and renders a dropdown
    #   in forms and in the admin.
    # - default=PATIENT: anyone who registers is a patient unless we say otherwise,
    #   so nobody can accidentally become a doctor or admin by signing up.
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.PATIENT)

    # Optional phone number (needed later for SMS/WhatsApp reminders).
    # blank=True means forms may leave it empty. For text fields Django stores ""
    # rather than NULL, which is the recommended convention.
    phone = models.CharField(max_length=20, blank=True)

    # @property lets us write user.is_patient (no parentheses) instead of a method call.
    # Views and templates will use these: {% if user.is_doctor %} ... {% endif %}
    @property
    def is_patient(self):
        # Compare against the constant, not the raw string "patient",
        # so a typo becomes an error instead of a silent bug.
        return self.role == self.Role.PATIENT

    @property
    def is_doctor(self):
        return self.role == self.Role.DOCTOR