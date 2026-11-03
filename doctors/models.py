from django.db import models

from django.conf import settings
from django.db import models


class Specialty(models.Model):
    # Name of a medical specialty, e.g. "Cardiology".
    # unique=True: the DB refuses duplicates.
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        # Without this the admin would say "Specialtys".
        verbose_name_plural = "specialties"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Doctor(models.Model):
    # One doctor profile per user account.
    # settings.AUTH_USER_MODEL points to our custom accounts.User.
    # limit_choices_to: forms and the admin only offer users with role="doctor".
    # CASCADE: deleting the user also deletes the profile.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "doctor"},
        related_name="doctor_profile",
    )

    # A doctor can have several specialties; a specialty has many doctors.
    specialties = models.ManyToManyField(Specialty, related_name="doctors", blank=True)

    # Short bio shown on the doctor's profile page.
    bio = models.TextField(blank=True)

    # Hide a doctor from booking without deleting their history.
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["user__last_name", "user__first_name"]

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username}"
