import os
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


def doctor_photo_path(instance, filename):
    """Build the upload path for a doctor's photo.

    Result: doctors/doctor-<user id>-<8 random chars>.<ext>
    - The user id shows whose photo it is.
    - The random part gives each upload a new URL, so browsers never show
      a stale cached photo after an update.
    - The original extension (.webp, .png, .jpg) is kept, lowercased.
    """
    ext = os.path.splitext(filename)[1].lower()
    return f"doctors/doctor-{instance.user_id}-{uuid.uuid4().hex[:8]}{ext}"


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

    # Doctor's photo, uploaded in the admin. Saved under MEDIA_ROOT with a
    # name built by doctor_photo_path(). Needs Pillow.
    # Optional: if empty, the templates show the doctor's initials.
    photo = models.ImageField(upload_to=doctor_photo_path, blank=True)

    # Hide a doctor from booking without deleting their history.
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["user__last_name", "user__first_name"]

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username}"

    def save(self, *args, **kwargs):
        # Remember the current photo file name before saving (existing doctors only).
        old_photo = None
        if self.pk:
            old_photo = (
                Doctor.objects.filter(pk=self.pk).values_list("photo", flat=True).first()
            )

        super().save(*args, **kwargs)

        # If the photo was replaced or cleared, delete the old file from disk
        # so unused photos don't pile up in media/doctors/.
        if old_photo and old_photo != self.photo.name:
            self.photo.storage.delete(old_photo)


class Availability(models.Model):
    # Days of the week. Numbers match Python's date.weekday():
    # Monday = 0 ... Sunday = 6, so we can compare them directly.
    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"

    # Which doctor this working block belongs to.
    # related_name lets us write doctor.availabilities.all().
    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="availabilities"
    )

    # Day of the week and the working hours on that day.
    weekday = models.PositiveSmallIntegerField(choices=Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()

    # Length of each appointment in minutes.
    slot_minutes = models.PositiveSmallIntegerField(default=30)

    class Meta:
        verbose_name_plural = "availabilities"
        ordering = ["doctor", "weekday", "start_time"]
        constraints = [
            # Database-level rule: a doctor cannot have two blocks starting
            # at the same time on the same weekday.
            models.UniqueConstraint(
                fields=["doctor", "weekday", "start_time"],
                name="unique_doctor_weekday_start",
            ),
        ]

    def clean(self):
        # Runs in forms and the admin.
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")
        if self.slot_minutes == 0:
            raise ValidationError("Slot length must be at least 1 minute.")

    def __str__(self):
        return (
            f"{self.doctor} - {self.get_weekday_display()} "
            f"{self.start_time:%H:%M}-{self.end_time:%H:%M}"
        )