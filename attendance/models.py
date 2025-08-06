from django.db import models
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from django.utils import timezone

from users.models import Student
from courses.models import ClassSession


class Attendance(models.Model):
    STATUS_CHOICES = [
        ("PRESENT", "Present"),
        ("ABSENT", "Absent"),
        ("EXCUSED", "Excused"),
    ]
    METHOD_CHOICES = [
        ("RFID", "RFID"),
        ("QR", "QR"),  # QR is optional second-factor if lecturer activates it
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendance_records")
    session = models.ForeignKey(ClassSession, on_delete=models.CASCADE, related_name="attendance_records")

    check_in_time = models.DateTimeField(blank=True, null=True)
    verification_method = models.CharField(max_length=10, choices=METHOD_CHOICES, blank=True, null=True)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default="ABSENT")
    marks_awarded = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Optional two-step verification
    is_verified = models.BooleanField(default=False)  # True for RFID-only when QR inactive, or after QR finalize
    qr_token = models.CharField(max_length=64, blank=True, null=True, unique=True)  # only used if per-student QR

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "session")
        indexes = [
            models.Index(fields=["session", "student"]),
            models.Index(fields=["status"]),
            models.Index(fields=["verification_method"]),
        ]
        ordering = ["session", "student"]

    def __str__(self):
        return f"{self.student.index_number} - {self.session} [{self.status}]"

    def ensure_qr_token(self):
        if not self.qr_token:
            self.qr_token = get_random_string(40)

    def clean(self):
        # Guardrail: EXCUSED requires a PermissionRequest for this student+session
        if self.status == "EXCUSED":
            if not PermissionRequest.objects.filter(student=self.student, session=self.session).exists():
                raise ValidationError("EXCUSED requires a lecturer PermissionRequest.")

    # Convenience for RFID check-in (views/services will call this)
    def mark_present_rfid(self, pending_qr: bool):
        self.status = "PRESENT"
        self.verification_method = "RFID"
        self.check_in_time = self.check_in_time or timezone.now()
        self.is_verified = not pending_qr


class PermissionRequest(models.Model):
    """
    Lecturer-entered excuse. Creating this record is the ONLY way a student becomes EXCUSED.
    Your view/signal should upsert Attendance to EXCUSED immediately.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="permission_requests")
    session = models.ForeignKey(ClassSession, on_delete=models.CASCADE, related_name="permission_requests")
    reason  = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "session")
        indexes = [models.Index(fields=["session", "student"])]
        ordering = ["session", "student"]

    def __str__(self):
        return f"Perm {self.student.index_number} @ {self.session}"
