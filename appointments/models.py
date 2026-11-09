from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models

from doctors.models import Doctor


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    # PROTECT: you cannot delete a doctor or patient who has appointments,
    # so medical history is never lost by accident.
    doctor = models.ForeignKey(
        Doctor, on_delete=models.PROTECT, related_name="appointments"
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="appointments",
        limit_choices_to={"role": "patient"},
    )

    # When the appointment starts (timezone-aware). The end is start plus the
    # availability's slot_minutes, so we don't store it.
    start_time = models.DateTimeField()

    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.CONFIRMED
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start_time"]
        constraints = [
            # THE most important rule: the database itself refuses two active
            # appointments for the same doctor at the same time.
            # Cancelled ones are excluded, so a cancelled slot can be rebooked.
            models.UniqueConstraint(
                fields=["doctor", "start_time"],
                condition=~models.Q(status="cancelled"),
                name="unique_active_doctor_start",
            ),
        ]

    def __str__(self):
        return f"{self.patient} with {self.doctor} at {self.start_time:%Y-%m-%d %H:%M}"